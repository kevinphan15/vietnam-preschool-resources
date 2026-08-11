#!/usr/bin/env python3
"""Sinh 2 bảng HTML (danh bạ trường + danh bạ học phí) từ raw-list.tsv."""
import html
import re
import sys
import unicodedata
from pathlib import Path

RAW = Path(__file__).parent / "raw-list.tsv"


def strip_tones(s: str) -> str:
    # đ/Đ là chữ cái riêng, NFD không tách được -> phải thay tay trước
    s = s.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


# Khu vực: từ khoá (không dấu) -> nhãn hiển thị. Khớp theo độ dài giảm dần.
REGION = {
    # TP. Hồ Chí Minh
    "quan 12": "Quận 12, TP.HCM", "quan 11": "Quận 11, TP.HCM", "quan 10": "Quận 10, TP.HCM",
    "quan 1": "Quận 1, TP.HCM", "quan 2": "Quận 2, TP.HCM", "quan 3": "Quận 3, TP.HCM",
    "quan 4": "Quận 4, TP.HCM", "quan 5": "Quận 5, TP.HCM", "quan 6": "Quận 6, TP.HCM",
    "quan 7": "Quận 7, TP.HCM", "quan 8": "Quận 8, TP.HCM", "quan 9": "Quận 9, TP.HCM",
    "binh thanh": "Bình Thạnh, TP.HCM", "tan binh": "Tân Bình, TP.HCM",
    "tan phu": "Tân Phú, TP.HCM", "phu nhuan": "Phú Nhuận, TP.HCM",
    "go vap": "Gò Vấp, TP.HCM", "thu duc": "TP. Thủ Đức, TP.HCM",
    "binh tan": "Bình Tân, TP.HCM", "binh chanh": "Bình Chánh, TP.HCM",
    "nha be": "Nhà Bè, TP.HCM", "hoc mon": "Hóc Môn, TP.HCM", "cu chi": "Củ Chi, TP.HCM",
    "an phu dong": "Quận 12, TP.HCM", "hiep thanh": "Quận 12, TP.HCM",
    "thanh loc": "Quận 12, TP.HCM", "ha huy giap": "Quận 12, TP.HCM", "to ky": "Quận 12, TP.HCM",
    "thao dien": "Quận 2, TP.HCM", "an phu": "Quận 2, TP.HCM", "vista verde": "Quận 2, TP.HCM",
    "new city": "Quận 2, TP.HCM", "lexington": "Quận 2, TP.HCM", "quoc huong": "Quận 2, TP.HCM",
    "binh an": "Quận 2, TP.HCM", "tu xuong": "Quận 3, TP.HCM", "vo thi sau": "Quận 3, TP.HCM",
    "him lam": "Quận 7, TP.HCM", "phu my hung": "Quận 7, TP.HCM", "tan quy": "Quận 7, TP.HCM",
    "luxcity": "Quận 7, TP.HCM", "phu thuan": "Quận 7, TP.HCM",
    "bau cat": "Tân Bình, TP.HCM", "tan son hoa": "Tân Bình, TP.HCM",
    "le lu": "Tân Phú, TP.HCM", "hoa thanh": "Tân Phú, TP.HCM", "son ky": "Tân Phú, TP.HCM",
    "le dinh thu": "Tân Phú, TP.HCM", "melody": "Tân Phú, TP.HCM",
    "ten lua": "Bình Tân, TP.HCM", "ehome": "Bình Tân, TP.HCM", "tecco": "Bình Tân, TP.HCM",
    "binh tri dong": "Bình Tân, TP.HCM", "an lac": "Bình Tân, TP.HCM",
    "richmond city": "Bình Thạnh, TP.HCM", "wilton": "Bình Thạnh, TP.HCM",
    "opal": "Bình Thạnh, TP.HCM", "phuoc kien": "Nhà Bè, TP.HCM",
    "hung phat": "Nhà Bè, TP.HCM", "long truong": "TP. Thủ Đức, TP.HCM",
    "phu huu": "TP. Thủ Đức, TP.HCM", "binh tho": "TP. Thủ Đức, TP.HCM",
    "nguyen thi dinh": "TP. Thủ Đức, TP.HCM", "cat lai": "TP. Thủ Đức, TP.HCM",
    "tuoi hoa": "TP. Thủ Đức, TP.HCM", "nam long": "TP. Thủ Đức, TP.HCM",
    "pham the hien": "Quận 8, TP.HCM", "ta quang buu": "Quận 8, TP.HCM",
    "phuoc binh": "TP. Thủ Đức, TP.HCM", "ho chi minh": "TP. Hồ Chí Minh",
    # Hà Nội
    "cau giay": "Cầu Giấy, Hà Nội", "ha dong": "Hà Đông, Hà Nội", "ba dinh": "Ba Đình, Hà Nội",
    "dong da": "Đống Đa, Hà Nội", "hai ba trung": "Hai Bà Trưng, Hà Nội",
    "hoang mai": "Hoàng Mai, Hà Nội", "long bien": "Long Biên, Hà Nội",
    "nam tu liem": "Nam Từ Liêm, Hà Nội", "bac tu liem": "Bắc Từ Liêm, Hà Nội",
    "tay ho": "Tây Hồ, Hà Nội", "hoan kiem": "Hoàn Kiếm, Hà Nội",
    "gia lam": "Gia Lâm, Hà Nội", "hoai duc": "Hoài Đức, Hà Nội",
    "dong anh": "Đông Anh, Hà Nội", "thanh tri": "Thanh Trì, Hà Nội",
    "soc son": "Sóc Sơn, Hà Nội", "chuong my": "Chương Mỹ, Hà Nội",
    "thanh oai": "Thanh Oai, Hà Nội", "ha noi": "Hà Nội",
    "linh dam": "Hoàng Mai, Hà Nội", "yen so": "Hoàng Mai, Hà Nội",
    "gamuda": "Hoàng Mai, Hà Nội", "timescity": "Hai Bà Trưng, Hà Nội",
    "vinh tuy": "Hai Bà Trưng, Hà Nội", "minh khai": "Hai Bà Trưng, Hà Nội",
    "pham dinh ho": "Hai Bà Trưng, Hà Nội", "ngoai giao doan": "Bắc Từ Liêm, Hà Nội",
    "pham van dong": "Bắc Từ Liêm, Hà Nội", "geleximco": "Hoài Đức, Hà Nội",
    "an khanh": "Hoài Đức, Hà Nội", "trung hoa": "Cầu Giấy, Hà Nội",
    "xuan thuy": "Cầu Giấy, Hà Nội", "dich vong": "Cầu Giấy, Hà Nội",
    "me tri": "Nam Từ Liêm, Hà Nội", "quoc tu giam": "Đống Đa, Hà Nội",
    "lang thuong": "Đống Đa, Hà Nội", "van chuong": "Đống Đa, Hà Nội",
    "yen lang": "Đống Đa, Hà Nội", "hang bot": "Đống Đa, Hà Nội",
    "ngoc khanh": "Ba Đình, Hà Nội", "linh lang": "Ba Đình, Hà Nội",
    "hoang hoa tham": "Ba Đình, Hà Nội", "ly nam de": "Hoàn Kiếm, Hà Nội",
    "yet kieu": "Hoàn Kiếm, Hà Nội", "to ngoc van": "Tây Hồ, Hà Nội",
    "van phuc": "Hà Đông, Hà Nội", "nhan chinh": "Thanh Xuân, Hà Nội",
    "thuong dinh": "Thanh Xuân, Hà Nội", "nguyen tuan": "Thanh Xuân, Hà Nội",
    "khai son city": "Long Biên, Hà Nội", "ocean park": "Gia Lâm, Hà Nội",
    "nam cuong": "Hà Đông, Hà Nội", "le lai": "Hà Đông, Hà Nội",
    "hoang van thu": "Hà Nội", "an trach": "Đống Đa, Hà Nội",
    "than dong viet": "Hà Nội", "thang long": "Hà Nội",
    # Tỉnh/thành khác
    "hai phong": "Hải Phòng", "van giang": "Văn Giang, Hưng Yên",
    "ecopark": "Văn Giang, Hưng Yên", "ben luc": "Bến Lức, Long An",
    "binh duong": "Bình Dương", "dong nai": "Đồng Nai",
}
REGION_KEYS = sorted(REGION, key=len, reverse=True)

# 'thạnh xuân' (Q12 HCM) vs 'thanh xuân' (Hà Nội) — chỉ phân biệt được khi còn dấu.
TONED_REGION = {"thạnh xuân": "Quận 12, TP.HCM", "thanh xuân": "Thanh Xuân, Hà Nội"}

LEVELS = [
    ("Trung tâm giáo dục đặc biệt", ("giao duc dac biet", "chuyen biet", "can thiep som")),
    ("Trung tâm ngoại ngữ", ("tieng anh", "anh ngu", "ngoai ngu", "ielts")),
    ("Trung tâm kỹ năng", ("mc nhi", "vietskill")),
    ("Liên cấp", ("lien cap", "thcs", "he thong giao duc", "vao lop 1", "tien tieu hoc")),
    ("Tiểu học", ("tieu hoc",)),
]

PROGRAMS = [
    ("Montessori", ("montessori",)),
    ("Steiner / Waldorf", ("steiner", "waldorf")),
    ("Reggio Emilia", ("reggio",)),
    ("STEAM", ("steam",)),
    ("Song ngữ", ("song ngu", "bilingual")),
    ("Quốc tế", ("quoc te", "international")),
]


def classify(key: str, table, default: str) -> str:
    for label, needles in table:
        if any(n in key for n in needles):
            return label
    return default


def region_of(name: str, slug: str) -> str:
    low = name.lower()
    for toned, label in TONED_REGION.items():
        if toned in low:
            return label
    # đệm khoảng trắng 2 đầu + so khớp trọn từ, tránh 'binh tho' khớp nhầm 'binh thoi'
    key = f" {strip_tones(low)} {slug.replace('-', ' ')} "
    for k in REGION_KEYS:
        if f" {k} " in key:
            return REGION[k]
    return "—"


def name_from_slug(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.split("-"))


def row(cells) -> str:
    tds = "\n".join(f"  <td>{c}</td>" for c in cells)
    return f"<tr>\n{tds}\n</tr>"


def link(url: str, text: str) -> str:
    return (f'<a href="{html.escape(url)}" target="_blank" '
            f'rel="noopener noreferrer">{html.escape(text)}</a>')


def table(headers, rows) -> str:
    head = "\n".join(f"  <th>{h}</th>" for h in headers)
    body = "\n".join(rows)
    return (f"<table>\n<thead>\n<tr>\n{head}\n</tr>\n</thead>\n"
            f"<tbody>\n{body}\n</tbody>\n</table>")


def main() -> None:
    schools, fees = [], []
    seen = set()
    for line in RAW.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        name, _, url = line.partition("\t")
        name, url = name.strip(), url.strip()
        if not url or url in seen:
            continue
        seen.add(url)
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        if "/truong/" in url:
            display = name.title() if name else name_from_slug(slug)
            key = strip_tones(f"{name} {slug.replace('-', ' ')}".lower())
            schools.append(row([
                html.escape(display), link(url, display), region_of(name, slug),
                classify(key, LEVELS, "Mầm non"),
                classify(key, PROGRAMS, "Chương trình GDMN quốc gia"),
                "Đã lập chỉ mục",
            ]))
        else:
            area = re.sub(r"^học phí mầm non\s+", "", name, flags=re.I).strip()
            area = area.title().replace("Tp. ", "TP. ")
            fees.append(row([
                html.escape(area), link(url, f"Học phí mầm non {area}"),
                "Mầm non", "Khảo sát học phí", "Đã lập chỉ mục",
            ]))

    out = Path(__file__).parent
    (out / "table-truong.html").write_text(table(
        ["Cơ sở giáo dục", "Đường dẫn", "Khu vực", "Loại hình", "Chương trình", "Trạng thái"],
        schools), encoding="utf-8")
    (out / "table-hoc-phi.html").write_text(table(
        ["Địa bàn", "Đường dẫn", "Cấp học", "Loại dữ liệu", "Trạng thái"],
        fees), encoding="utf-8")
    print(f"truong={len(schools)} hoc-phi={len(fees)}")


def demo() -> None:
    assert region_of("mầm non ánh sao mai thạnh xuân", "truong-mam-non-anh-sao-mai-thanh-xuan") == "Quận 12, TP.HCM"
    assert region_of("mầm non o'hana thanh xuân", "truong-mam-non-o-hana-quan-thanh-xuan") == "Thanh Xuân, Hà Nội"
    # "phường 11" là phường, không suy ra được quận -> để trống thay vì đoán bừa
    assert region_of("mầm non bánh táo 11", "x-phuong-11") == "—"
    assert region_of("mầm non kid's club bình thới quận 11", "co-so-binh-thoi") == "Quận 11, TP.HCM"
    assert region_of("abc", "xyz") == "—"
    assert classify("truong tieu hoc song ngu wellspring", LEVELS, "Mầm non") == "Tiểu học"
    assert classify("trung tam tieng anh apax", LEVELS, "Mầm non") == "Trung tâm ngoại ngữ"
    assert classify("mam non clover montessori", PROGRAMS, "x") == "Montessori"
    print("demo ok")


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else main()
