import pandas as pd
import re
from collections import Counter

def generate_keyword_summary(file_path, output_path):
    # Cargar datos
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    
    # Palabras clave de interés (basadas en el contexto de Ecuador 2025)
    keywords = [
        'noboa', 'luisa', 'fraude', 'cne', 'iza', 'correismo', 
        'voto', 'elecciones', 'crisis', 'gobierno', 'seguridad',
        'transparencia', 'campaña'
    ]
    
    summary_data = []
    
    for kw in keywords:
        # Filtrar filas que contienen la palabra clave (case insensitive)
        mask = df['content'].str.contains(kw, case=False, na=False)
        subset = df[mask]
        
        count = len(subset)
        if count > 0:
            sentiment_counts = subset['sentiment_label'].value_counts().to_dict()
            top_sentiment = subset['sentiment_label'].mode()[0] if not subset.empty else "N/A"
            
            summary_data.append({
                'Palabra Clave': kw.capitalize(),
                'Menciones': count,
                'Sentimiento Predominante': top_sentiment.capitalize(),
                'Detalle (Pos/Neu/Neg)': f"{sentiment_counts.get('positive', 0)} / {sentiment_counts.get('neutral', 0)} / {sentiment_counts.get('negative', 0)}"
            })
    
    summary_df = pd.DataFrame(summary_data).sort_values(by='Menciones', ascending=False)
    
    # Generar el reporte en Markdown
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Resumen de Análisis de Sentimiento por Palabras Clave\n\n")
        f.write(f"**Total de registros analizados:** {len(df)}\n\n")
        
        f.write("## Distribución General de Sentimientos\n")
        gen_counts = df['sentiment_label'].value_counts()
        for label, count in gen_counts.items():
            f.write(f"- **{label.capitalize()}:** {count} ({round(count/len(df)*100, 2)}%)\n")
        
        f.write("\n## Análisis por Términos Relevantes\n\n")
        f.write(summary_df.to_markdown(index=False))
        
        f.write("\n\n---\n*Reporte generado para validación de resultados - Proyecto Tesis Percepcion IA*")

    print(f"Reporte generado exitosamente en: {output_path}")

if __name__ == "__main__":
    input_csv = 'data/processed/social_sentiment.csv'
    output_md = 'outputs/latest/tables/resumen_sentimiento_keywords.md'
    generate_keyword_summary(input_csv, output_md)
