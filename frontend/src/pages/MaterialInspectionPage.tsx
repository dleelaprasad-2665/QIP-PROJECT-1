import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  Camera,
  ScanSearch,
  CheckCircle2,
  AlertTriangle,
  Boxes,
  ArrowRight,
  RefreshCw,
  Layers,
  Info,
  Check,
  Download,
  X
} from 'lucide-react';
import { api } from '../api/client';
import { AIAnalysisResult, DefectItem } from '../types';
import { ConditionBadge, RecommendationBadge, SeverityBadge } from '../components/common/Badge';
import { ScoreGauge } from '../components/common/ScoreGauge';

interface MaterialInspectionPageProps {
  onSavedToInventory?: () => void;
}

export const MaterialInspectionPage: React.FC<MaterialInspectionPageProps> = ({ onSavedToInventory }) => {
  // Upload & Camera state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);

  // Analysis state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState<string>('');
  const [result, setResult] = useState<AIAnalysisResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // View state: 'annotated' | 'original'
  const [viewMode, setViewMode] = useState<'annotated' | 'original'>('annotated');

  // Confirmation & Inventory Save Form
  const [quantity, setQuantity] = useState<number>(1);
  const [unit, setUnit] = useState<string>('pieces');
  const [siteLocation, setSiteLocation] = useState<string>('Central Yard A');
  const [projectName, setProjectName] = useState<string>('EcoBuild Site 1');
  const [inspectionNotes, setInspectionNotes] = useState<string>('');
  const [isSaving, setIsSaving] = useState(false);
  const [savedItemId, setSavedItemId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const currentRequestIdRef = useRef<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelected = (file: File) => {
    // Abort any prior in-flight analysis
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    const newReqId = 'req_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
    currentRequestIdRef.current = newReqId;

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    setResult(null);
    setErrorMsg(null);
    setSavedItemId(null);
    stopCamera();
  };

  // WebCam controls
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      setCameraStream(stream);
      setIsCameraActive(true);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Camera access error:', err);
      setErrorMsg('Camera access could not be initialized. Please check browser permissions or upload an image file.');
    }
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => track.stop());
      setCameraStream(null);
    }
    setIsCameraActive(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `capture_${Date.now()}.jpg`, { type: 'image/jpeg' });
        handleFileSelected(file);
      }
    }, 'image/jpeg', 0.92);
  };

  // Run AI Inspection
  const runAnalysis = async () => {
    if (!selectedFile) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    const reqId = 'req_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
    currentRequestIdRef.current = reqId;

    // Reset previous prediction immediately for this new run
    setResult(null);
    setErrorMsg(null);
    setIsAnalyzing(true);

    try {
      setAnalysisStatus('Evaluating image resolution and clarity...');
      await new Promise(r => setTimeout(r, 150));

      setAnalysisStatus('Executing material classification and defect segmentation...');
      const res = await api.analyzeMaterialImage(
        selectedFile,
        siteLocation,
        projectName,
        reqId,
        abortController.signal
      );

      // Verify response belongs to this exact current request
      if (currentRequestIdRef.current !== reqId) {
        console.warn('Discarding stale analysis response:', res.request_id);
        return;
      }

      setAnalysisStatus('Computing circular reusability recommendations...');
      await new Promise(r => setTimeout(r, 150));

      setResult(res);

      if (res.inspection_id) {
        setSavedItemId(res.inspection_id);
        if (onSavedToInventory) onSavedToInventory();
      }

      // Auto-set appropriate unit based on material category
      if (res.material_category === 'Cement') setUnit('bags');
      else if (res.material_category === 'Steel rods / Reinforcement bars') setUnit('tons');
      else if (res.material_category === 'Tiles') setUnit('sq.m');
      else if (res.material_category === 'Pipes') setUnit('meters');
      else if (['Sand', 'Aggregates'].includes(res.material_category)) setUnit('cu.m');
      else setUnit('pieces');

    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('Analysis request aborted for new upload.');
        return;
      }
      setErrorMsg(err.message || 'Inspection failed. Please ensure the backend AI server is running.');
    } finally {
      if (currentRequestIdRef.current === reqId) {
        setIsAnalyzing(false);
        setAnalysisStatus('');
      }
    }
  };

  // Save to Digital Inventory
  const handleSaveToInventory = async () => {
    if (!result || !result.is_valid_construction_material) return;

    try {
      setIsSaving(true);
      const saved = await api.saveToInventory({
        material_category: result.material_category,
        confidence: result.material_confidence,
        condition: result.condition,
        condition_score: result.condition_score,
        recommendation: result.recommendation,
        recommendation_reason: result.recommendation_reason,
        suggested_next_step: result.suggested_next_step,
        defects: result.detected_defects,
        original_image_path: result.original_image_url,
        annotated_image_path: result.annotated_image_url,
        quantity: Number(quantity) || 1,
        unit,
        site_location: siteLocation,
        project_name: projectName,
        inspection_status: 'Verified',
        notes: inspectionNotes
      });

      setSavedItemId(saved.id);
      if (onSavedToInventory) onSavedToInventory();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to save record to inventory.');
    } finally {
      setIsSaving(false);
    }
  };

  const clearSelection = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    currentRequestIdRef.current = null;
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setErrorMsg(null);
    setSavedItemId(null);
    stopCamera();
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Page Heading */}
      <div>
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">
          Construction Material Quality Inspection
        </h1>
        <p className="text-gray-500 text-xs mt-1">
          Upload or capture a material photograph to identify category, inspect visible structural defects, and receive preliminary reuse recommendations.
        </p>
      </div>

      {/* Main Grid: Upload & Inspection Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Image Upload & Camera (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-gray-100">
              <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700">Material Source Image</h3>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    if (isCameraActive) stopCamera();
                    else startCamera();
                  }}
                  className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg font-medium border transition-colors ${
                    isCameraActive
                      ? 'bg-rose-50 text-rose-700 border-rose-200'
                      : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                  }`}
                >
                  <Camera className="w-3.5 h-3.5 text-blue-600" />
                  <span>{isCameraActive ? 'Cancel Camera' : 'Use Camera'}</span>
                </button>
              </div>
            </div>

            {/* Camera Viewport or Upload Dropzone */}
            {isCameraActive ? (
              <div className="relative rounded-lg overflow-hidden border border-blue-500 bg-black aspect-video flex items-center justify-center">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="w-full h-full object-cover"
                />
                <button
                  onClick={capturePhoto}
                  className="absolute bottom-3 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-3.5 py-1.5 rounded-lg shadow-md flex items-center gap-1.5"
                >
                  <Camera className="w-3.5 h-3.5" />
                  <span>Take Photo</span>
                </button>
              </div>
            ) : (
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => !previewUrl && fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center text-center transition-colors ${
                  previewUrl
                    ? 'border-gray-200 bg-gray-50/50'
                    : 'border-gray-300 hover:border-blue-500 bg-gray-50/80 hover:bg-blue-50/30 cursor-pointer'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files?.[0]) {
                      handleFileSelected(e.target.files[0]);
                    }
                    e.target.value = '';
                  }}
                />

                {previewUrl ? (
                  <div className="relative w-full aspect-video rounded-lg overflow-hidden border border-gray-200 bg-black">
                    <img
                      src={previewUrl}
                      alt="Uploaded preview"
                      className="w-full h-full object-contain"
                    />
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        clearSelection();
                      }}
                      className="absolute top-2 right-2 bg-white/90 hover:bg-white text-gray-700 p-1.5 rounded-md shadow-xs text-xs font-medium flex items-center gap-1"
                      title="Remove image"
                    >
                      <X className="w-3.5 h-3.5 text-rose-600" />
                      <span>Change</span>
                    </button>
                  </div>
                ) : (
                  <div className="space-y-2 py-4">
                    <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 mx-auto flex items-center justify-center">
                      <UploadCloud className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-gray-800">
                        Drag and drop material image here, or click to browse
                      </p>
                      <p className="text-[11px] text-gray-500 mt-0.5">
                        Accepts JPG, PNG, WEBP from device or site camera
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Error Message */}
            {errorMsg && (
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Analyze Material Button */}
            <button
              onClick={runAnalysis}
              disabled={!selectedFile || isAnalyzing}
              className={`w-full py-2.5 px-4 rounded-lg font-semibold text-xs flex items-center justify-center gap-2 transition-colors shadow-xs ${
                !selectedFile || isAnalyzing
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-white" />
                  <span>{analysisStatus || 'Analyzing Material...'}</span>
                </>
              ) : (
                <>
                  <ScanSearch className="w-4 h-4" />
                  <span>Analyze Material</span>
                </>
              )}
            </button>
          </div>

          {/* Supported Categories Reference Card */}
          <div className="bg-white border border-gray-200 rounded-xl p-4 text-xs space-y-2 shadow-xs">
            <span className="text-[11px] uppercase font-bold tracking-wider text-gray-500 block">
              Supported Material Categories:
            </span>
            <div className="flex flex-wrap gap-1.5 pt-0.5">
              {[
                'Cement', 'Bricks', 'Concrete blocks', 'Steel rods / Reinforcement bars', 'Wooden planks',
                'Tiles', 'Sand', 'Aggregates', 'Glass', 'Pipes'
              ].map((c) => (
                <span key={c} className="text-[11px] bg-gray-50 text-gray-700 px-2 py-0.5 rounded border border-gray-200">
                  {c}
                </span>
              ))}
            </div>
            <p className="text-[11px] text-gray-400 pt-1">
              Images that do not contain supported construction materials will be rejected.
            </p>
          </div>
        </div>

        {/* Right Column: AI Analysis Result Display (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {!result && !isAnalyzing && (
            <div className="bg-white border border-gray-200 border-dashed rounded-xl p-12 flex flex-col items-center justify-center text-center min-h-[420px] shadow-xs">
              <div className="w-12 h-12 rounded-xl bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-400 mb-3">
                <ScanSearch className="w-6 h-6 text-gray-400" />
              </div>
              <h3 className="text-sm font-bold text-gray-800">Awaiting Material Image</h3>
              <p className="text-xs text-gray-500 max-w-sm mt-1">
                Upload or capture a material photo on the left and click "Analyze Material" to begin automated defect inspection and reusability assessment.
              </p>
            </div>
          )}

          {isAnalyzing && (
            <div className="bg-white border border-gray-200 rounded-xl p-12 flex flex-col items-center justify-center text-center min-h-[420px] space-y-4 shadow-xs">
              <div className="w-10 h-10 rounded-full border-3 border-gray-200 border-t-blue-600 animate-spin" />
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-gray-900">
                  Processing Computer Vision Pipeline
                </h4>
                <p className="text-xs text-blue-600 font-mono">
                  {analysisStatus}
                </p>
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {!result.is_valid_construction_material ? (
                <div className="bg-white border border-rose-200 rounded-xl p-5 text-gray-800 space-y-2 shadow-xs">
                  <div className="flex items-center gap-2 text-rose-700 font-bold text-xs">
                    <AlertTriangle className="w-4 h-4 text-rose-600" />
                    <span>Unrecognized or Unclear Image</span>
                  </div>
                  <p className="text-xs text-gray-700">
                    {result.message || 'Unable to confidently identify this material. Please upload a clearer image or request manual inspection.'}
                  </p>
                  <p className="text-[11px] text-gray-500">
                    Please upload a sharp, well-lit photo of an approved construction material category.
                  </p>
                </div>
              ) : (
                <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-xs space-y-5">
                  {/* Category & Confidence Header */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-gray-100 gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">
                          Identified Material Category
                        </span>
                        {result.inspection_id && (
                          <span className="text-[10px] font-mono font-bold bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded border border-blue-200">
                            ID: {result.inspection_id}
                          </span>
                        )}
                      </div>
                      <div className="text-lg font-bold text-gray-900 flex items-center gap-2 mt-0.5">
                        <span>{result.material_category}</span>
                        <span className="text-xs font-mono font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded">
                          {result.material_confidence}% Confidence
                        </span>
                      </div>
                    </div>

                    <div className="text-xs font-mono text-gray-500">
                      Inference Time: {result.inference_time_ms} ms
                    </div>
                  </div>

                  {/* Condition & Recommendation Row */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <ScoreGauge score={result.condition_score} />

                    <div className="bg-gray-50/70 p-4 rounded-xl border border-gray-200 flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold uppercase tracking-wider text-gray-500">
                            Reusability Recommendation
                          </span>
                          <RecommendationBadge recommendation={result.recommendation} size="md" />
                        </div>
                        <p className="text-xs text-gray-700 mt-2 leading-relaxed">
                          {result.recommendation_reason}
                        </p>
                      </div>
                      <div className="mt-2.5 pt-2 border-t border-gray-200 text-xs text-gray-600 flex items-start gap-1.5">
                        <ArrowRight className="w-3.5 h-3.5 shrink-0 mt-0.5 text-blue-600" />
                        <span><strong className="text-gray-900">Next Step:</strong> {result.suggested_next_step}</span>
                      </div>
                    </div>
                  </div>

                  {/* Visual Defect Evidence */}
                  <div className="space-y-2 pt-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold uppercase tracking-wider text-gray-600 flex items-center gap-1.5">
                        <Layers className="w-3.5 h-3.5 text-blue-600" />
                        <span>Visual Defect Localization</span>
                      </span>
                      <div className="flex items-center bg-gray-100 p-0.5 rounded border border-gray-200 text-xs">
                        <button
                          onClick={() => setViewMode('annotated')}
                          className={`px-2 py-0.5 rounded font-medium transition-colors ${
                            viewMode === 'annotated'
                              ? 'bg-white text-gray-900 shadow-xs'
                              : 'text-gray-500 hover:text-gray-900'
                          }`}
                        >
                          Defect Map
                        </button>
                        <button
                          onClick={() => setViewMode('original')}
                          className={`px-2 py-0.5 rounded font-medium transition-colors ${
                            viewMode === 'original'
                              ? 'bg-white text-gray-900 shadow-xs'
                              : 'text-gray-500 hover:text-gray-900'
                          }`}
                        >
                          Original
                        </button>
                      </div>
                    </div>

                    <div className="rounded-lg overflow-hidden border border-gray-200 aspect-video bg-black relative">
                      <img
                        src={api.getImageUrl(viewMode === 'annotated' ? result.annotated_image_url : result.original_image_url)}
                        alt="Material defect map"
                        className="w-full h-full object-contain"
                      />
                    </div>
                  </div>

                  {/* Defects Breakdown List */}
                  <div className="space-y-2 pt-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold uppercase tracking-wider text-gray-600">
                        Identified Defects ({result.detected_defects.length})
                      </span>
                      <ConditionBadge condition={result.condition} size="sm" />
                    </div>

                    {result.detected_defects.length === 0 ? (
                      <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>No visible structural defects detected. Material appears in good condition.</span>
                      </div>
                    ) : (
                      <div className="space-y-1.5">
                        {result.detected_defects.map((defect: DefectItem, idx: number) => (
                          <div
                            key={idx}
                            className="bg-gray-50 border border-gray-200 p-3 rounded-lg flex items-center justify-between text-xs"
                          >
                            <div className="space-y-0.5">
                              <div className="flex items-center gap-2">
                                <span className="font-semibold text-gray-900">{defect.name}</span>
                                <SeverityBadge severity={defect.severity} />
                              </div>
                              <p className="text-[11px] text-gray-500">{defect.description}</p>
                            </div>
                            <div className="text-right font-mono shrink-0">
                              <span className="text-gray-700 font-semibold">{defect.confidence}%</span>
                              {defect.bbox && (
                                <span className="block text-[10px] text-gray-400">
                                  [{defect.bbox.x}, {defect.bbox.y}, {defect.bbox.width}x{defect.bbox.height}]
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Safety Disclaimer */}
                  <div className="p-3 rounded-lg bg-gray-50 border border-gray-200 text-gray-600 text-[11px] leading-relaxed flex items-start gap-2">
                    <Info className="w-4 h-4 text-gray-400 shrink-0 mt-0.5" />
                    <span>{result.safety_disclaimer}</span>
                  </div>

                  {/* Save to Digital Inventory Form */}
                  <div className="pt-3 border-t border-gray-200 space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center gap-1.5">
                        <Boxes className="w-4 h-4 text-blue-600" />
                        <span>Save to Material Inventory</span>
                      </h4>
                      {savedItemId && (
                        <span className="text-xs font-mono text-emerald-700 font-semibold flex items-center gap-1">
                          <Check className="w-3.5 h-3.5" /> Saved: {savedItemId}
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                      <div>
                        <label className="block text-gray-600 text-xs font-medium mb-1">
                          Quantity
                        </label>
                        <input
                          type="number"
                          min="0.1"
                          step="any"
                          value={quantity}
                          onChange={(e) => setQuantity(Number(e.target.value))}
                          className="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-gray-900 font-mono focus:outline-none focus:border-blue-600"
                        />
                      </div>

                      <div>
                        <label className="block text-gray-600 text-xs font-medium mb-1">
                          Unit of Measurement
                        </label>
                        <select
                          value={unit}
                          onChange={(e) => setUnit(e.target.value)}
                          aria-label="Unit of measurement"
                          className="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-600"
                        >
                          <option value="pieces">pieces</option>
                          <option value="tons">tons</option>
                          <option value="kg">kg</option>
                          <option value="sq.m">sq.m</option>
                          <option value="cu.m">cu.m</option>
                          <option value="meters">meters</option>
                          <option value="bags">bags</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-gray-600 text-xs font-medium mb-1">
                          Yard / Site Location
                        </label>
                        <select
                          value={siteLocation}
                          onChange={(e) => setSiteLocation(e.target.value)}
                          aria-label="Construction Site or Yard Location"
                          className="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-600"
                        >
                          <option value="Central Yard A">Central Yard A</option>
                          <option value="Skyline Tower Phase 2">Skyline Tower Phase 2</option>
                          <option value="Metro Rail Extension Yard 4">Metro Rail Extension Yard 4</option>
                          <option value="Harbor Logistic Hub">Harbor Logistic Hub</option>
                          <option value="EcoCity Residential Block B">EcoCity Residential Block B</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-gray-600 text-xs font-medium mb-1">
                        Inspection Notes
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Visual quality screening completed. Staged for site engineer verification."
                        value={inspectionNotes}
                        onChange={(e) => setInspectionNotes(e.target.value)}
                        className="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-gray-900 placeholder-gray-400 text-xs focus:outline-none focus:border-blue-600"
                      />
                    </div>

                    {/* Action Buttons: Save & Download PDF */}
                    <div className="flex flex-col sm:flex-row items-center gap-2 pt-1">
                      <button
                        onClick={handleSaveToInventory}
                        disabled={isSaving || Boolean(savedItemId)}
                        className={`w-full sm:w-auto flex-1 py-2 px-4 rounded-lg font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors ${
                          savedItemId
                            ? 'bg-emerald-50 text-emerald-800 border border-emerald-200 cursor-default'
                            : 'bg-blue-600 hover:bg-blue-700 text-white shadow-xs'
                        }`}
                      >
                        <Boxes className="w-4 h-4" />
                        <span>{savedItemId ? 'Saved to Inventory ✓' : 'Save to Inventory'}</span>
                      </button>

                      {savedItemId && (
                        <a
                          href={api.getPdfReportUrl(savedItemId)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="w-full sm:w-auto py-2 px-4 rounded-lg font-semibold text-xs bg-gray-100 hover:bg-gray-200 text-gray-800 border border-gray-200 flex items-center justify-center gap-1.5 transition-colors"
                        >
                          <Download className="w-4 h-4 text-blue-600" />
                          <span>Download Report (PDF)</span>
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
