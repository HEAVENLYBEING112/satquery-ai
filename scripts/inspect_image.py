import sys
import argparse
from engine.geospatial.loader import RasterLoader, RasterLoaderError

def main():
    parser = argparse.ArgumentParser(description="SatQuery Image Inspector")
    parser.add_argument("filepath", type=str, help="Path to image file to inspect")
    parser.add_argument("--modality", type=str, help="Optional modality override")
    
    args = parser.parse_args()
    loader = RasterLoader()
    
    try:
        asset = loader.load(args.filepath, modality_override=args.modality)
    except RasterLoaderError as e:
        print(f"Error loading image: {e}")
        sys.exit(1)
        
    print("=" * 50)
    print("SATQUERY IMAGE INSPECTOR")
    print("=" * 50)
    print()
    print("File:")
    print(asset.filename)
    print()
    print("Format:")
    print(asset.format)
    print()
    print("Dimensions:")
    print(f"{asset.width} × {asset.height}")
    print()
    print("Bands:")
    print(asset.bands)
    print()
    
    if asset.metadata.get("dtype"):
        print("Dtype:")
        print(asset.metadata["dtype"])
        print()
        
    print("CRS:")
    print(asset.crs if asset.crs else "None")
    print()
    
    if asset.resolution:
        print("Resolution:")
        print(asset.resolution)
        print()
        
    if asset.bbox:
        print("Bounds:")
        print(asset.bbox)
        print()
        
    print("Detected modality:")
    print(asset.modality.upper())
    print()
    
    if "nodata" in asset.metadata:
        print("Nodata:")
        print(asset.metadata["nodata"])
        print()
        
    print("Status:")
    print("VALID")
    print("=" * 50)

if __name__ == "__main__":
    main()
