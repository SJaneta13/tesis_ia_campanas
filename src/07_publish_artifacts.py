# src/07_publish_artifacts.py
from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from datetime import datetime
import json

def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

def copy_tree_clean(src_dir: Path, dst_dir: Path, patterns: list[str] | None = None) -> int:
    """
    Copia un conjunto de archivos de src_dir a dst_dir replicando estructura relativa.
    Si patterns=None copia TODO el tree.
    Retorna #archivos copiados.
    """
    if not src_dir.exists():
        return 0

    count = 0
    if patterns is None:
        # Copia completa (limpia el destino primero)
        if dst_dir.exists():
            shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)
        # Contar archivos
        return sum(1 for _ in dst_dir.rglob("*") if _.is_file())

    # Copia selectiva por patrones
    for pat in patterns:
        for f in src_dir.rglob(pat):
            if f.is_file():
                rel = f.relative_to(src_dir)
                copy_file(f, dst_dir / rel)
                count += 1
    return count

def ensure_clean_dir(dir_path: Path) -> None:
    dir_path.mkdir(parents=True, exist_ok=True)

def main():
    p = argparse.ArgumentParser(description="Publica artefactos (Noticias + Encuestas) a backend/public/ para la plataforma.")
    p.add_argument("--backend-public", default="backend/public", help="Destino base para publicar (por defecto backend/public).")

    # Noticias (dashboard)
    p.add_argument("--news-outdir", default="outputs/visualization/news",
                   help="Carpeta donde dashboard_news.py guardó .html/.png (y opcional .csv).")

    # Encuestas (outputs/latest)
    p.add_argument("--surveys-latest", default="outputs/latest",
                   help="Carpeta outputs/latest generada por 03_modeling.py (y 03a/03b).")

    # Flags
    p.add_argument("--publish-news", action="store_true", help="Publicar módulo Noticias.")
    p.add_argument("--publish-surveys", action="store_true", help="Publicar módulo Encuestas.")
    p.add_argument("--clean", action="store_true", help="Limpiar destino del módulo antes de copiar.")
    args = p.parse_args()

    backend_public = Path(args.backend_public)
    news_src = Path(args.news_outdir)
    surveys_src = Path(args.surveys_latest)

    news_dst = backend_public / "news"
    surveys_dst = backend_public / "surveys"

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not args.publish_news and not args.publish_surveys:
        # Si no pasan flags, publica ambos por defecto (más cómodo)
        args.publish_news = True
        args.publish_surveys = True

    # =========================
    # PUBLICAR NOTICIAS
    # =========================
    if args.publish_news:
        if not news_src.exists():
            raise FileNotFoundError(f"No existe news-outdir: {news_src}. Primero ejecuta dashboard_news.py.")

        if args.clean and news_dst.exists():
            shutil.rmtree(news_dst)

        ensure_clean_dir(news_dst)

        # Copiamos HTML/PNG/CSV (si luego haces Opción B, ya quedan listos)
        copied = 0
        for ext in ["*.html", "*.png", "*.csv", "*.json"]:
            for f in news_src.rglob(ext):
                if f.is_file():
                    copy_file(f, news_dst / f.name)  # plano, sin subcarpetas
                    copied += 1

        # manifest simple
        (news_dst / "MANIFEST.txt").write_text(
            f"Publicado: {ts}\nOrigen: {news_src}\nArchivos: {copied}\n",
            encoding="utf-8"
        )

        (news_dst / "MANIFEST.json").write_text(
        json.dumps({
            "module": "news",
            "published_at": ts,
            "source": str(news_src),
            "destination": str(news_dst),
            "files": copied
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
        )

        print(f"[DONE] Noticias publicadas en: {news_dst} | archivos: {copied}")

    # =========================
    # PUBLICAR ENCUESTAS
    # =========================
    if args.publish_surveys:
        if not surveys_src.exists():
            raise FileNotFoundError(f"No existe surveys-latest: {surveys_src}. Ejecuta primero src/03_modeling.py (genera outputs/latest).")

        if args.clean and surveys_dst.exists():
            shutil.rmtree(surveys_dst)

        # Copia completa para que tengas tablas/figuras/modelos disponibles
        copied = copy_tree_clean(surveys_src, surveys_dst, patterns=None)

        # manifest simple
        (surveys_dst / "MANIFEST.txt").write_text(
            f"Publicado: {ts}\nOrigen: {surveys_src}\nArchivos: {copied}\n",
            encoding="utf-8"
        )

        (surveys_dst / "MANIFEST.json").write_text(
        json.dumps({
            "module": "surveys",
            "published_at": ts,
            "source": str(surveys_src),
            "destination": str(surveys_dst),
            "files": copied
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
        )
        
        print(f"[DONE] Encuestas publicadas en: {surveys_dst} | archivos: {copied}")

    print(f"[OK] Publicación terminada. Base: {backend_public}")

if __name__ == "__main__":
    main()
