#!/usr/bin/env python3
"""Merge Chinese strings from tools/zh_pack.py into translation_catalog.csv.

Does not touch the ISO or jp column. Re-run after adding pack entries.
Existing non-empty zh is kept unless --force.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zh_pack import by_id, by_jp, copy_jp_prefixes, fill_generated  # noqa: E402
from zh_story_sun import by_id as story_by_id  # noqa: E402
from zh_story_mon import by_id as story_mon_by_id  # noqa: E402
from zh_story_tue import by_id as story_tue_by_id  # noqa: E402
from zh_story_wed import by_id as story_wed_by_id  # noqa: E402
from zh_story_thu import by_id as story_thu_by_id  # noqa: E402
from zh_story_fri import by_id as story_fri_by_id  # noqa: E402
from zh_story_gho import by_id as story_gho_by_id  # noqa: E402
from zh_story_ear import by_id as story_ear_by_id  # noqa: E402
from zh_story_solo import by_id as story_solo_by_id  # noqa: E402
from zh_story_cal import by_id as story_cal_by_id  # noqa: E402
from zh_story_col import by_id as story_col_by_id  # noqa: E402
from zh_story_call import by_id as story_call_by_id  # noqa: E402
from zh_story_gen import by_id as story_gen_by_id  # noqa: E402
from zh_story_mini import by_id as story_mini_by_id  # noqa: E402
from zh_story_end import by_id as story_end_by_id  # noqa: E402
from zh_story_comp import by_id as story_comp_by_id  # noqa: E402
from zh_dung_egg import by_id as dung_egg_by_id  # noqa: E402
from zh_dung_planets import by_id as dung_planets_by_id  # noqa: E402
from zh_dung_ui import by_id as dung_ui_by_id  # noqa: E402
from zh_dung_cameo1 import by_id as dung_cameo1_by_id  # noqa: E402
from zh_dung_cameo2 import by_id as dung_cameo2_by_id  # noqa: E402
from zh_dung_cameo3 import by_id as dung_cameo3_by_id  # noqa: E402
from zh_dung_cameo4 import by_id as dung_cameo4_by_id  # noqa: E402
from zh_dung_cameo5 import by_id as dung_cameo5_by_id  # noqa: E402
from zh_dung_cameo6 import by_id as dung_cameo6_by_id  # noqa: E402
from zh_dung_cameo7 import by_id as dung_cameo7_by_id  # noqa: E402
from zh_dung_tekken import by_id as dung_tekken_by_id  # noqa: E402
from zh_dic_guest import by_id as dic_guest_by_id  # noqa: E402
from zh_dic_u18 import by_id as dic_u18_by_id  # noqa: E402
from zh_dic_u91 import by_id as dic_u91_by_id  # noqa: E402
from zh_dic_u180 import by_id as dic_u180_by_id  # noqa: E402
from zh_dic_u251 import by_id as dic_u251_by_id  # noqa: E402
from zh_dic_u336 import by_id as dic_u336_by_id  # noqa: E402
from zh_dic_eg_cl import by_id as dic_eg_cl_by_id  # noqa: E402
from zh_dic_eg_cv import by_id as dic_eg_cv_by_id  # noqa: E402
from zh_dic_eg_du import by_id as dic_eg_du_by_id  # noqa: E402
from zh_dic_eg_ev import by_id as dic_eg_ev_by_id  # noqa: E402
from zh_dic_eg_le import by_id as dic_eg_le_by_id  # noqa: E402
from zh_dic_eg_ms import by_id as dic_eg_ms_by_id  # noqa: E402
from zh_dic_eg_pk import by_id as dic_eg_pk_by_id  # noqa: E402
from zh_dic_eg_pw import by_id as dic_eg_pw_by_id  # noqa: E402
from zh_dic_eg_we import by_id as dic_eg_we_by_id  # noqa: E402
from zh_eg_names import by_id as eg_names_by_id  # noqa: E402
from zh_eg_atk import by_id as eg_atk_by_id  # noqa: E402
from zh_eg_rank import by_id as eg_rank_by_id  # noqa: E402
from zh_eg_battle_jp import by_jp as eg_battle_by_jp  # noqa: E402
from zh_eg_du_bat1 import by_id as eg_du_bat1_by_id  # noqa: E402
from zh_eg_du_bat2 import by_id as eg_du_bat2_by_id  # noqa: E402
from zh_eg_du_bat3 import by_id as eg_du_bat3_by_id  # noqa: E402
from zh_eg_bo_season import by_id as eg_bo_season_by_id  # noqa: E402
from zh_eg_bo_boil import by_id as eg_bo_boil_by_id  # noqa: E402
from zh_eg_bo_rest import by_id as eg_bo_rest_by_id  # noqa: E402
from zh_eg_we_bat1 import by_id as eg_we_bat1_by_id  # noqa: E402
from zh_eg_we_bat2 import by_id as eg_we_bat2_by_id  # noqa: E402
from zh_eg_pk_bat1 import by_id as eg_pk_bat1_by_id  # noqa: E402
from zh_eg_pk_bat2 import by_id as eg_pk_bat2_by_id  # noqa: E402
from zh_eg_ev_bat1 import by_id as eg_ev_bat1_by_id  # noqa: E402
from zh_eg_ev_bat2 import by_id as eg_ev_bat2_by_id  # noqa: E402
from zh_eg_cl_bat1 import by_id as eg_cl_bat1_by_id  # noqa: E402
from zh_eg_cl_bat2 import by_id as eg_cl_bat2_by_id  # noqa: E402
from zh_eg_ms_bat1 import by_id as eg_ms_bat1_by_id  # noqa: E402
from zh_eg_ms_bat2 import by_id as eg_ms_bat2_by_id  # noqa: E402
from zh_eg_cv_bat1 import by_id as eg_cv_bat1_by_id  # noqa: E402
from zh_eg_cv_bat2 import by_id as eg_cv_bat2_by_id  # noqa: E402
from zh_eg_pw_bat1 import by_id as eg_pw_bat1_by_id  # noqa: E402
from zh_eg_pw_bat2 import by_id as eg_pw_bat2_by_id  # noqa: E402
from zh_eg_le_bat1 import by_id as eg_le_bat1_by_id  # noqa: E402
from zh_eg_le_bat2 import by_id as eg_le_bat2_by_id  # noqa: E402
from zh_eg_tg_bat import by_id as eg_tg_bat_by_id  # noqa: E402
from zh_eg_cu_bat import by_id as eg_cu_bat_by_id  # noqa: E402
from zh_menu_trump import by_id as menu_trump_by_id  # noqa: E402
from zh_trump_bat import by_id as trump_bat_by_id  # noqa: E402
from zh_gameover import by_id as gameover_by_id  # noqa: E402
from zh_tutorial import by_id as tutorial_by_id  # noqa: E402
from zh_boss_menu import by_id as boss_menu_by_id  # noqa: E402
from zh_general import by_id as general_by_id  # noqa: E402
from zh_okunote import by_id as okunote_by_id  # noqa: E402
from zh_misc_rest import by_id as misc_rest_by_id  # noqa: E402
from zh_ev_plo import by_id as ev_plo_by_id  # noqa: E402
from zh_planet_plates import by_id as planet_plates_by_id  # noqa: E402
from zh_basis import by_id as basis_by_id  # noqa: E402
from zh_rest_ui import by_id as rest_ui_by_id  # noqa: E402
from zh_debug_dg import by_id as debug_dg_by_id  # noqa: E402
from zh_debug_field import by_id as debug_field_by_id  # noqa: E402
from zh_test_rest import by_id as test_rest_by_id  # noqa: E402
from zh_sysmes_debug import by_id as sysmes_debug_by_id  # noqa: E402

ROOT = Path("/home/ubuntu/translation/extracted")
CSV = ROOT / "translation_catalog.csv"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--force",
        action="store_true",
        help="overwrite zh that are already filled",
    )
    args = ap.parse_args()

    rows: list[dict[str, str]] = []
    with CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or ["id", "jp", "zh", "notes"]
        for row in reader:
            rows.append(row)

    gen = fill_generated()
    idmap = {**gen, **by_id(), **story_by_id(), **story_mon_by_id(), **story_tue_by_id(), **story_wed_by_id(), **story_thu_by_id(), **story_fri_by_id(), **story_gho_by_id(), **story_ear_by_id(), **story_solo_by_id(), **story_cal_by_id(), **story_col_by_id(), **story_call_by_id(), **story_gen_by_id(), **story_mini_by_id(), **story_end_by_id(), **story_comp_by_id(), **dung_egg_by_id(), **dung_planets_by_id(), **dung_ui_by_id(), **dung_cameo1_by_id(), **dung_cameo2_by_id(), **dung_cameo3_by_id(), **dung_cameo4_by_id(), **dung_cameo5_by_id(), **dung_cameo6_by_id(), **dung_cameo7_by_id(), **dung_tekken_by_id(), **dic_guest_by_id(), **dic_u18_by_id(), **dic_u91_by_id(), **dic_u180_by_id(), **dic_u251_by_id(), **dic_u336_by_id(), **dic_eg_cl_by_id(), **dic_eg_cv_by_id(), **dic_eg_du_by_id(), **dic_eg_ev_by_id(), **dic_eg_le_by_id(), **dic_eg_ms_by_id(), **dic_eg_pk_by_id(), **dic_eg_pw_by_id(), **dic_eg_we_by_id(), **eg_names_by_id(), **eg_atk_by_id(), **eg_rank_by_id(), **eg_du_bat1_by_id(), **eg_du_bat2_by_id(), **eg_du_bat3_by_id(), **eg_bo_season_by_id(), **eg_bo_boil_by_id(), **eg_bo_rest_by_id(), **eg_we_bat1_by_id(), **eg_we_bat2_by_id(), **eg_pk_bat1_by_id(), **eg_pk_bat2_by_id(), **eg_ev_bat1_by_id(), **eg_ev_bat2_by_id(), **eg_cl_bat1_by_id(), **eg_cl_bat2_by_id(), **eg_ms_bat1_by_id(), **eg_ms_bat2_by_id(), **eg_cv_bat1_by_id(), **eg_cv_bat2_by_id(), **eg_pw_bat1_by_id(), **eg_pw_bat2_by_id(), **eg_le_bat1_by_id(), **eg_le_bat2_by_id(), **eg_tg_bat_by_id(), **eg_cu_bat_by_id(), **menu_trump_by_id(), **trump_bat_by_id(), **gameover_by_id(), **tutorial_by_id(), **boss_menu_by_id(), **general_by_id(), **okunote_by_id(), **misc_rest_by_id(), **ev_plo_by_id(), **planet_plates_by_id(), **basis_by_id(), **rest_ui_by_id(), **debug_dg_by_id(), **debug_field_by_id(), **test_rest_by_id(), **sysmes_debug_by_id()}
    jpmap = {**by_jp(), **eg_battle_by_jp()}
    prefixes = copy_jp_prefixes()

    n_id = n_jp = n_copy = n_skip = 0
    for row in rows:
        sid = row["id"]
        jp = row.get("jp") or ""
        cur = row.get("zh") or ""
        if cur and not args.force:
            n_skip += 1
            continue
        zh = None
        if sid in idmap:
            zh = idmap[sid]
            n_id += 1
        else:
            for pfx in prefixes:
                if sid == pfx or sid.startswith(pfx + "#") or sid.startswith(pfx + "_"):
                    zh = jp
                    n_copy += 1
                    break
        if zh is None and jp in jpmap:
            zh = jpmap[jp]
            n_jp += 1
        if zh is not None:
            row["zh"] = zh

    with CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    filled = sum(1 for r in rows if (r.get("zh") or "").strip())
    print(
        f"zh filled {filled}/{len(rows)}  "
        f"by_id {n_id}  by_jp {n_jp}  copy_jp {n_copy}  kept {n_skip}"
    )


if __name__ == "__main__":
    main()
