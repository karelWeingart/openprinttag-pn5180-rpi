export interface PaginationInfo {
  total: number;
  total_pages: number;
  page: number;
  page_size: number;
}

export interface TagData {
  tag_uid: string | null;
  material_type: string | null;
  material_name: string | null;
  manufacturer: string | null;
  primary_color_hex: string | null;
}
