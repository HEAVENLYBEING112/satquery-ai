// frontend/src/components/viewer/ImageViewer.tsx
import React, { useState, useRef } from 'react';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
  RotateCcw,
  Compass,
  Crosshair,
} from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { BoundingBoxOverlay } from './BoundingBoxOverlay';
import { ChangeMaskOverlay } from './ChangeMaskOverlay';
import { TemporalSlider } from './TemporalSlider';
import { CrossModalToggle } from './CrossModalToggle';
import { ViewerLegend } from './ViewerLegend';
import { EmptyState } from '../ui/EmptyState';
import { SAMPLE_OPTICAL_PORT, SAMPLE_SAR_PORT, SAMPLE_TEMPORAL_T1, SAMPLE_TEMPORAL_T2 } from '../../api/mock/mockData';

export const ImageViewer: React.FC = () => {
  const {
    workflowMode,
    files,
    currentResult,
    viewerLayer,
    crossModalActiveLayer,
    selectedBoundingBox,
  } = useAppStore();

  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState({ x: 0, y: 0 });
  const [cursorCoords, setCursorCoords] = useState<{ x: number; y: number; lat: string; lon: string } | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const viewerContainerRef = useRef<HTMLDivElement>(null);

  const handleZoomIn = () => setZoomLevel((z) => Math.min(4, +(z + 0.25).toFixed(2)));
  const handleZoomOut = () => setZoomLevel((z) => Math.max(0.5, +(z - 0.25).toFixed(2)));
  const handleReset = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
  };

  const toggleFullscreen = () => {
    if (!viewerContainerRef.current) return;
    if (!isFullscreen) {
      if (viewerContainerRef.current.requestFullscreen) {
        viewerContainerRef.current.requestFullscreen();
      }
      setIsFullscreen(true);
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
      setIsFullscreen(false);
    }
  };

  const onMouseDown = (e: React.MouseEvent) => {
    if (workflowMode === 'temporal') return;
    setIsPanning(true);
    setStartPan({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
  };

  const onMouseMove = (e: React.MouseEvent) => {
    if (!viewerContainerRef.current) return;
    const rect = viewerContainerRef.current.getBoundingClientRect();
    const px = Math.round(((e.clientX - rect.left) / rect.width) * 600);
    const py = Math.round(((e.clientY - rect.top) / rect.height) * 600);

    const lat = (17.68 + (py / 600) * 0.04).toFixed(4);
    const lon = (83.21 + (px / 600) * 0.04).toFixed(4);

    setCursorCoords({ x: px, y: py, lat: `${lat}° N`, lon: `${lon}° E` });

    if (isPanning) {
      setPanOffset({
        x: e.clientX - startPan.x,
        y: e.clientY - startPan.y,
      });
    }
  };

  const onMouseUp = () => setIsPanning(false);

  const opticalFile = files.find((f) => f.modality === 'optical') || files[0];
  const sarFile = files.find((f) => f.modality === 'sar');
  const t1File = files.find((f) => f.role === 'before') || files[0];
  const t2File = files.find((f) => f.role === 'after') || files[1] || files[0];

  const primaryPreviewUrl =
    workflowMode === 'cross_modal'
      ? crossModalActiveLayer === 'sar'
        ? sarFile?.previewUrl || SAMPLE_SAR_PORT
        : opticalFile?.previewUrl || SAMPLE_OPTICAL_PORT
      : opticalFile?.previewUrl || SAMPLE_OPTICAL_PORT;

  const boundingBoxes = currentResult?.evidence?.[0]?.bounding_boxes || [];
  const changeMask = currentResult?.evidence?.[0]?.change_mask || null;

  if (files.length === 0) {
    return (
      <div className="h-full flex flex-col justify-center">
        <EmptyState
          title="SATELLITE VIEWPORT INACTIVE"
          description="Load satellite imagery or select a preset on the left to activate telemetry."
        />
      </div>
    );
  }

  return (
    <div
      ref={viewerContainerRef}
      className="flex flex-col h-full rounded-xl bg-[#050505] border border-white/10 shadow-2xl overflow-hidden relative font-mono"
    >
      {/* Top Floating Control Bar */}
      <div className="absolute top-2.5 left-2.5 right-2.5 z-30 flex flex-wrap items-center justify-between gap-2 pointer-events-auto">
        {/* Left: Viewport Mode */}
        <div>
          {workflowMode === 'cross_modal' ? (
            <CrossModalToggle />
          ) : (
            <div className="px-2.5 py-1 rounded bg-[#090909]/90 border border-white/10 text-[10px] text-white flex items-center gap-2">
              <Compass className="w-3 h-3 text-[#38BDF8]" />
              <span className="font-bold tracking-wider">
                {workflowMode === 'temporal'
                  ? 'TEMPORAL OBSERVATION: T1 vs T2'
                  : opticalFile?.name.toUpperCase() || 'SATELLITE VIEWPORT'}
              </span>
            </div>
          )}
        </div>

        {/* Right: Square Minimal Action Controls */}
        <div className="flex items-center gap-1 p-1 rounded bg-[#090909]/90 border border-white/10">
          <button
            onClick={handleZoomIn}
            className="w-7 h-7 rounded bg-[#111111] border border-white/10 text-white hover:border-[#38BDF8] hover:text-[#38BDF8] flex items-center justify-center transition-colors cursor-pointer text-xs"
            title="Zoom In (+)"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <span className="text-[10px] px-1 text-[#A0A0A0] min-w-[32px] text-center">
            {Math.round(zoomLevel * 100)}%
          </span>
          <button
            onClick={handleZoomOut}
            className="w-7 h-7 rounded bg-[#111111] border border-white/10 text-white hover:border-[#38BDF8] hover:text-[#38BDF8] flex items-center justify-center transition-colors cursor-pointer text-xs"
            title="Zoom Out (−)"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleReset}
            className="w-7 h-7 rounded bg-[#111111] border border-white/10 text-white hover:border-[#38BDF8] hover:text-[#38BDF8] flex items-center justify-center transition-colors cursor-pointer text-xs"
            title="Reset View (⟳)"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={toggleFullscreen}
            className="w-7 h-7 rounded bg-[#111111] border border-white/10 text-white hover:border-[#38BDF8] hover:text-[#38BDF8] flex items-center justify-center transition-colors cursor-pointer text-xs"
            title="Fullscreen (⛶)"
          >
            {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Main Interactive Canvas Area */}
      <div
        className="flex-1 relative overflow-hidden bg-[#050505] flex items-center justify-center cursor-grab active:cursor-grabbing"
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
      >
        {workflowMode === 'temporal' ? (
          <TemporalSlider
            beforeUrl={t1File?.previewUrl || SAMPLE_TEMPORAL_T1}
            afterUrl={t2File?.previewUrl || SAMPLE_TEMPORAL_T2}
            beforeDate={t1File?.acquisitionDate || '2024-01-15 (T1)'}
            afterDate={t2File?.acquisitionDate || '2024-08-10 (T2)'}
          />
        ) : (
          <div
            className="relative transition-transform duration-75 select-none"
            style={{
              transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
              transformOrigin: 'center center',
            }}
          >
            {/* Satellite Raster Image */}
            <img
              src={primaryPreviewUrl}
              alt="Satellite Remote Sensing Observation"
              className="max-w-[560px] max-h-[560px] rounded object-contain pointer-events-none"
              draggable={false}
            />

            {/* Overlays */}
            {(viewerLayer === 'evidence' || viewerLayer === 'grounding' || viewerLayer === 'segmentation') && (
              <BoundingBoxOverlay boxes={boundingBoxes} />
            )}

            {(viewerLayer === 'evidence' || viewerLayer === 'change_mask') && (
              <ChangeMaskOverlay changeMask={changeMask} />
            )}
          </div>
        )}

        {/* Bottom Coordinates HUD */}
        <div className="absolute bottom-2.5 left-2.5 z-20 flex items-center gap-2 pointer-events-none text-[10px]">
          <div className="px-2 py-0.5 rounded bg-[#090909]/90 border border-white/10 text-white flex items-center gap-2">
            <Crosshair className="w-3 h-3 text-[#38BDF8]" />
            <span>
              PX: {cursorCoords?.x ?? 300}, {cursorCoords?.y ?? 300}
            </span>
            <span className="text-[#666666]">|</span>
            <span className="text-[#38BDF8]">
              {cursorCoords?.lat ?? '17.7021° N'}, {cursorCoords?.lon ?? '83.2245° E'}
            </span>
          </div>

          <div className="hidden sm:flex px-2 py-0.5 rounded bg-[#090909]/90 border border-white/10 text-[#22C55E]">
            EPSG:32644 (UTM Zone 44N)
          </div>
        </div>

        {/* Bounding Box Detail Popover */}
        {selectedBoundingBox && (
          <div className="absolute top-14 right-3 z-30 p-2.5 rounded bg-[#090909] border border-sky-400/50 text-xs shadow-2xl max-w-xs">
            <div className="flex items-center justify-between pb-1 mb-1 border-b border-white/10">
              <span className="font-bold text-[#38BDF8]">{selectedBoundingBox.label}</span>
              <span className="text-[9px] px-1 py-0.2 rounded bg-[#1C1C1C] text-white">
                {selectedBoundingBox.source}
              </span>
            </div>
            <div className="text-[10px] text-[#A0A0A0] space-y-0.5">
              <div>COORDS: [{selectedBoundingBox.coordinates.join(', ')}]</div>
              <div>TYPE: {selectedBoundingBox.coordinate_type}</div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Layer Controls */}
      <div className="p-1.5 border-t border-white/10 bg-[#090909] z-20">
        <ViewerLegend />
      </div>
    </div>
  );
};
