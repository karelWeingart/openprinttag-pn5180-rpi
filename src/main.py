from pn5180_openprinttag import Pn5180OpenPrintTag


def main():
    """Main function to read and display OpenPrintTag data."""
    print("OpenPrintTag Reader - Starting...")
    print("-" * 50)
    
    try:

        reader = Pn5180OpenPrintTag()
        print("✓ PN5180 initialized")
        

        print("\nSearching for tags...")
        _uids = reader.inventoryCmd()
        
        if not _uids or not _uids[0]:
            print("✗ No tags found")
            return
        
        _uid = _uids[0]
        print(f"✓ Found tag with UID: {_uid}")
        
        print("\nReading OpenPrintTag data...")
        _tag_data = reader.read_openprinttag(_uid)
        print("✓ Tag data parsed successfully")
        
        print("\n" + "=" * 50)
        print("TAG INFORMATION")
        print("=" * 50)
        
        if _tag_data.main:
            print("\n[Main Region]")
            if _tag_data.main.material_name:
                print(f"  Material: {_tag_data.main.material_name}")
            if _tag_data.main.brand_name:
                print(f"  Brand: {_tag_data.main.brand_name}")
            if _tag_data.main.material_type:
                print(f"  Type: {_tag_data.main.material_type}")
            if _tag_data.main.primary_color:
                print(f"  Color: {_tag_data.main.primary_color}")
            if _tag_data.main.nominal_full_length:
                print(f"  Length: {_tag_data.main.nominal_full_length} mm")
            if _tag_data.main.nominal_netto_full_weight:
                print(f"  Weight: {_tag_data.main.nominal_netto_full_weight} g")
        
        if _tag_data.aux:
            print("\n[Aux Region]")
            if _tag_data.aux.consumed_weight:
                print(f"  Consumed: {_tag_data.aux.consumed_weight} g")
            if _tag_data.aux.workgroup:
                print(f"  Workgroup: {_tag_data.aux.workgroup}")
        
        if _tag_data.meta:
            print("\n[Meta Region]")
            print(f"  Main region: offset={_tag_data.meta.main_region_offset}, size={_tag_data.meta.main_region_size}")
        
        # Export as JSON
        print("\n" + "=" * 50)
        print("JSON Export:")
        print("=" * 50)
        print(_tag_data.model_dump_json(indent=2, exclude_none=True))
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n" + "-" * 50)
        print("Done!")


if __name__ == "__main__":
    main()

