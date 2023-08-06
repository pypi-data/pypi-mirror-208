import uuid
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field

from models.db import get_cursor
from aida_tools.utils import generate_id

cursor = get_cursor()
TABLE_NAME = "item"


class Item(BaseModel):

    id: Optional[str] = Field(default_factory=generate_id)
    module_id: int = Field(default=8) # <---------------------------- default=8
    folder_id: str = Field(default=None)
    published: Optional[int] = Field(default=None)
    ogtd_id: Optional[int] = Field(default=None)
    sgtt: Optional[str] = Field(max_length=100)
    sgtt_ext: Optional[str] = Field(default=None)
    is_attributed: Optional[int] = Field(default=None)
    is_original: Optional[int] = Field(default=None)
    event_type_id: Optional[int] = Field(default=None)
    act_scene: Optional[str] = Field(default=None, max_length=100)
    title: Optional[str] = Field(default=None, max_length=100)
    autm_id: Optional[int] = Field(default=None)
    no_date: Optional[int] = Field(default=None)
    dts_from_dates_id: Optional[int] = Field(default=None)
    dts_to_dates_id: Optional[int] = Field(default=None)
    dts_t_id: Optional[int] = Field(default=None)
    graf_publ_dts_dates_id: Optional[int] = Field(default=None)
    dtm_id: Optional[int] = Field(default=None)
    medium_id: Optional[int] = Field(default=None)
    num_support: Optional[int] = Field(default=None)
    placing: Optional[str] = Field(default=None)
    story: Optional[str] = Field(default=None)
    story_archive: Optional[str] = Field(default=None)
    acquisition: Optional[str] = Field(default=None)
    ambit: Optional[str] = Field(default=None)
    increase: Optional[str] = Field(default=None)
    sort_criterion: Optional[str] = Field(default=None)
    access_conditions: Optional[str] = Field(default=None)
    mtc: Optional[str] = Field(default=None)
    misa: Optional[str] = Field(default=None)
    misl: Optional[str] = Field(default=None)
    integration_desc: Optional[str] = Field(default=None)
    has_autograph: Optional[int] = Field(default=None)
    has_number: Optional[int] = Field(default=None)
    integration_num: Optional[str] = Field(default=None)
    techn_rec_id: Optional[int] = Field(default=None)
    stcc: Optional[str] = Field(default=None)
    stcc_d_id: Optional[str] = Field(default=None)
    stcc_c_id: Optional[str] = Field(default=None)
    signature: Optional[str] = Field(default=None)
    signature_pre: Optional[str] = Field(default=None)
    inventory: Optional[str] = Field(default=None)
    acqt_id: Optional[int] = Field(default=None)
    genre_id: Optional[int] = Field(default=None)
    genre_let_id: Optional[int] = Field(default=None)
    record_published: Optional[int] = Field(default=None)
    publ_no_date: Optional[int] = Field(default=None)
    publ_dts_dates_id: Optional[int] = Field(default=None)
    publ_place_id: Optional[int] = Field(default=None)
    language: Optional[str] = Field(default=None)
    series: Optional[str] = Field(default=None)
    prod_dates_id: Optional[int] = Field(default=None)
    has_dist_date: Optional[int] = Field(default=None)
    dist_dts_from_dates_id: Optional[int] = Field(default=None)
    dist_dts_to_dates_id: Optional[int] = Field(default=None)
    copyright_dates_id: Optional[int] = Field(default=None)
    record_code: Optional[str] = Field(default=None)
    duration: Optional[timedelta] = Field(default=None)
    is_around: Optional[int] = Field(default=None)
    is_exactly: Optional[int] = Field(default=None)
    mod_rec_id: Optional[int] = Field(default=None)
    signal_rec_id: Optional[int] = Field(default=None)
    note_signal: Optional[str] = Field(default=None)
    note_technical: Optional[str] = Field(default=None)
    note_technical_extra: Optional[str] = Field(default=None)
    note_record: Optional[str] = Field(default=None)
    note_content: Optional[str] = Field(default=None)
    note_conservation: Optional[str] = Field(default=None)
    acqd_dates_id: Optional[int] = Field(default=None)
    fill_status: Optional[str] = Field(default="parziale")
    is_lended: Optional[int] = Field(default=None)
    lend_from_dates_id: Optional[int] = Field(default=None)
    lend_to_dates_id: Optional[int] = Field(default=None)
    key_rel_place: Optional[str] = Field(default=None)
    medium_brand_id: Optional[int] = Field(default=None)
    model_id: Optional[int] = Field(default=None)
    flange_brand_id: Optional[int] = Field(default=None)
    flange_material_id: Optional[int] = Field(default=None)
    flange_size_id: Optional[int] = Field(default=None)
    case_material_id: Optional[int] = Field(default=None)
    case_medium_brand_id: Optional[int] = Field(default=None)
    wrapping_id: Optional[int] = Field(default=None)
    tape_size_id: Optional[int] = Field(default=None)
    speed_id: Optional[int] = Field(default=None)
    num_channels: Optional[int] = Field(default=None)
    num_tracks: Optional[int] = Field(default=None)
    equalisation_id: Optional[int] = Field(default=None)
    noise_id: Optional[int] = Field(default=None)
    hertz_id: Optional[int] = Field(default=None)
    audio_resolution_id: Optional[int] = Field(default=None)
    audiofile_format_id: Optional[int] = Field(default=None)
    transfer_dates_id: Optional[int] = Field(default=None)
    init_data: Optional[str] = Field(default=None)
    arch_procedure_id: Optional[int] = Field(default=None)
    video_format_id: Optional[int] = Field(default=None)
    tv_standard_id: Optional[int] = Field(default=None)
    aspect_ratio_id: Optional[int] = Field(default=None)
    audiov_resolution_id: Optional[int] = Field(default=None)
    mtx_id: Optional[int] = Field(default=None)
    foto_mtx_id: Optional[int] = Field(default=None)
    fps_id: Optional[int] = Field(default=None)
    audiov_compression_id: Optional[int] = Field(default=None)
    audio_compression_id: Optional[int] = Field(default=None)
    audiov_bitrate_id: Optional[int] = Field(default=None)
    audio_bitrate_id: Optional[int] = Field(default=None)
    is_sound: Optional[int] = Field(default=None)
    audio_mod_rec_id: Optional[int] = Field(default=None)
    audio_num_channels: Optional[int] = Field(default=None)
    audio_signal_rec_id: Optional[int] = Field(default=None)
    audio_note_signal: Optional[str] = Field(default=None)
    audio_noise_id: Optional[int] = Field(default=None)
    audio_hertz_id: Optional[int] = Field(default=None)
    copy_signature: Optional[str] = Field(default=None)
    copy_placing: Optional[str] = Field(default=None)
    copy_video_format_id: Optional[int] = Field(default=None)
    copy_tv_standard_id: Optional[int] = Field(default=None)
    copy_aspect_ratio_id: Optional[int] = Field(default=None)
    copy_audiov_resolution_id: Optional[int] = Field(default=None)
    copy_mtx_id: Optional[int] = Field(default=None)
    copy_fps_id: Optional[int] = Field(default=None)
    copy_audiov_compression_id: Optional[int] = Field(default=None)
    copy_audiov_bitrate_id: Optional[int] = Field(default=None)
    copy_video_duration: Optional[timedelta] = Field(default=None)
    copy_note_technical: Optional[str] = Field(default=None)
    copy_audio_note_technical: Optional[str] = Field(default=None)
    copy_hertz_id: Optional[int] = Field(default=None)
    copy_audio_resolution_id: Optional[int] = Field(default=None)
    copy_equalisation_id: Optional[int] = Field(default=None)
    copy_noise_id: Optional[int] = Field(default=None)
    subtitles_lang: Optional[str] = Field(default=None)
    region_code: Optional[str] = Field(default=None)
    audiovfile_signal_id: Optional[int] = Field(default=None)
    subject: Optional[str] = Field(default=None)
    abstract: Optional[str] = Field(default=None)
    edition: Optional[str] = Field(default=None)
    place_id: Optional[str] = Field(default=None)
    is_illustration: Optional[int] = Field(default=None)
    isbn_issn: Optional[str] = Field(default=None)
    num_copy: Optional[int] = Field(default=None)
    item_has_place_id: Optional[int] = Field(default=None)
    is_horizontal: Optional[int] = Field(default=None)
    mtcm_id: Optional[int] = Field(default=None)
    framing_id: Optional[int] = Field(default=None)
    file_compression: Optional[str] = Field(default=None)
    file_color: Optional[str] = Field(default=None)
    file_resolution: Optional[str] = Field(default=None)
    file_pixels: Optional[str] = Field(default=None)
    copyright: Optional[str] = Field(default=None)
    grou: Optional[str] = Field(default=None)
    role: Optional[str] = Field(default=None)
    genre_role: Optional[str] = Field(default=None)
    is_adult: Optional[int] = Field(default=None)
    num_components: Optional[int] = Field(default=None)
    mtcf_id: Optional[int] = Field(default=None)
    mtcc_id: Optional[int] = Field(default=None)
    mtcd_id: Optional[int] = Field(default=None)
    mtct_id: Optional[int] = Field(default=None)
    mtct_cost_id: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)
    format: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    note_internal: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    created_by: Optional[int] = Field(default=None)
    updated_by: Optional[int] = Field(default=None)
    miip: Optional[str] = Field(default=None)
    miia: Optional[str] = Field(default=None)
    miil: Optional[str] = Field(default=None)
    medium_cost_id: Optional[int] = Field(default=None)
    component_num: Optional[int] = Field(default=None)
    publ_num: Optional[str] = Field(default=None)
    publ_pag: Optional[str] = Field(default=None)
    doc_language: Optional[str] = Field(default=None)
    copy_is_sound: Optional[int] = Field(default=None)
    copy_audio_bitrate_id: Optional[int] = Field(default=None)

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "Item":
        """Create an Item from a list of values."""
        if with_id:
            return Item(**dict(zip(["id"] + Item._get_field_names(), values)))

        return Item(**dict(zip(Item._get_field_names(), values)))
   
    @staticmethod
    def _get_field_names() -> list[str]:
        return [field.name for field in Item.__fields__.values() if field.name != "id"]

    def _get_field_values(self) -> list[str]:
        return [getattr(self, field.name) for field in self.__fields__.values() if field.name != "id"]

    def save(self) -> "Item":
        values = [getattr(self, field.name) for field in self.__fields__.values()]

        cursor.execute(
            "INSERT INTO {} ({}) VALUES ({})".format(
                TABLE_NAME,
                ", ".join(["id"] + self._get_field_names()),
                ", ".join(["?"] * (len(self._get_field_names()) + 1))),
            values
        )

        return self

    def update(self) -> "Item":
        cursor.execute(
            "UPDATE {} SET {} WHERE id=?".format(
                TABLE_NAME,
                ", ".join(["{}=?".format(field) for field in self._get_field_names()])
            ),
            self._get_field_values() + [self.id]
        )

        return self

    @staticmethod
    def get(id: int) -> Optional["Item"]:
        cursor.execute("SELECT * FROM {} WHERE id=?".format(TABLE_NAME), (id,))
        row = cursor.fetchone()
        if row:
            return Item(**row)
        else:
            return None

    @staticmethod
    def get_all() -> list["Item"]:
        cursor.execute("SELECT * FROM {}".format(TABLE_NAME))
        rows = cursor.fetchall()
        return [Item.from_list(row, with_id=True) for row in rows]
