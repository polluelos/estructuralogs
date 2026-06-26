#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import csv
from pathlib import Path
from collections import defaultdict

def parse_markdown_table(file_path):
    """Parsear una tabla markdown sin dependencias externas"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_table = False
    for i, line in enumerate(lines):
        line = line.strip()
        if not line.startswith('|'):
            if in_table:
                break
            continue
        
        in_table = True
        if i < 2:  # Skip header y separator
            continue
        
        # Dividir por | y limpiar
        parts = [p.strip() for p in line.split('|')]
        parts = [p for p in parts if p]  # Eliminar strings vacíos
        
        if len(parts) == 4:
            try:
                account_id = int(parts[0])
                amount_str = parts[1].replace(',', '')
                amount = float(amount_str)
                country = parts[2]
                status = parts[3]
                
                data.append({
                    'Account ID': account_id,
                    'Amount (USD)': amount,
                    'Country': country,
                    'Status': status
                })
            except (ValueError, IndexError):
                continue
    
    return data

# Ruta del archivo
base_path = Path(__file__).parent
input_file = base_path / "transacciones_bancarias_120.md"

# Parsear los datos
data = parse_markdown_table(input_file)

print(f"Total de registros: {len(data)}")
print(f"Registros OK: {len([d for d in data if d['Status'] == 'OK'])}")
print(f"Registros KO: {len([d for d in data if d['Status'] == 'KO'])}")

# ============================================================
# PASO 1: Limpieza de logs (solo Status = OK)
# ============================================================

data_clean = [d for d in data if d['Status'] == 'OK']

# Guardar como markdown
output_md = base_path / "transacciones_limpias.md"
with open(output_md, 'w', encoding='utf-8') as f:
    f.write("# Transacciones Limpias\n\n")
    f.write("| Account ID | Amount (USD) | Country |\n")
    f.write("|---|---|---|\n")
    for row in data_clean:
        f.write(f"| {int(row['Account ID'])} | {row['Amount (USD)']:.2f} | {row['Country']} |\n")

print(f"\n✓ Fichero limpio generado: {output_md}")

# ============================================================
# PASO 2: Generación de CSV con sumas por cuenta
# ============================================================

sumas_dict = defaultdict(float)
for record in data_clean:
    sumas_dict[record['Account ID']] += record['Amount (USD)']

sumas_list = sorted([
    {'Account ID': k, 'Total': v}
    for k, v in sumas_dict.items()
], key=lambda x: x['Account ID'])

output_csv = base_path / "sumas_por_cuenta.csv"
with open(output_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Account ID', 'Total'])
    writer.writeheader()
    writer.writerows(sumas_list)

print(f"✓ CSV de sumas generado: {output_csv}")

# ============================================================
# PASO 3: Generación de XLS con gráficas
# ============================================================

try:
    from openpyxl import Workbook
    from openpyxl.chart import PieChart, BarChart, Reference
    
    wb = Workbook()
    wb.remove(wb.active)  # Eliminar hoja default
    
    # Hoja 1: Datos limpios
    ws1 = wb.create_sheet('Datos Limpios')
    ws1.append(['Account ID', 'Amount (USD)', 'Country'])
    for row in data_clean:
        ws1.append([row['Account ID'], row['Amount (USD)'], row['Country']])
    
    # Hoja 2: Sumas por cuenta
    ws2 = wb.create_sheet('Sumas por Cuenta')
    ws2.append(['Account ID', 'Total'])
    for row in sumas_list:
        ws2.append([row['Account ID'], row['Total']])
    
    # Hoja 3: Cuentas por país
    countries_clean = defaultdict(int)
    for record in data_clean:
        countries_clean[record['Country']] += 1
    
    ws3 = wb.create_sheet('Cuentas por País')
    ws3.append(['Country', 'Cantidad'])
    for country, count in sorted(countries_clean.items()):
        ws3.append([country, count])
    
    # Gráfica 1: Pie chart - Cuentas por país
    pie1 = PieChart()
    pie1.title = "Cantidad de Cuentas por País"
    labels1 = Reference(ws3, min_col=1, min_row=2, max_row=ws3.max_row)
    data1 = Reference(ws3, min_col=2, min_row=1, max_row=ws3.max_row)
    pie1.add_data(data1, titles_from_data=True)
    pie1.set_categories(labels1)
    ws3.add_chart(pie1, "D2")
    
    # Hoja 4: Transacciones por país (solo OK)
    countries_trans = defaultdict(int)
    for record in data:
        if record['Status'] == 'OK':
            countries_trans[record['Country']] += 1
    
    ws4 = wb.create_sheet('Trans. por País')
    ws4.append(['Country', 'Cantidad'])
    for country, count in sorted(countries_trans.items()):
        ws4.append([country, count])
    
    # Gráfica 2: Pie chart - Transacciones por país
    pie2 = PieChart()
    pie2.title = "Cantidad de Transacciones por País"
    labels2 = Reference(ws4, min_col=1, min_row=2, max_row=ws4.max_row)
    data2 = Reference(ws4, min_col=2, min_row=1, max_row=ws4.max_row)
    pie2.add_data(data2, titles_from_data=True)
    pie2.set_categories(labels2)
    ws4.add_chart(pie2, "D2")
    
    # Hoja 5: Top 10 cuentas
    top_10 = sorted(sumas_list, key=lambda x: x['Total'], reverse=True)[:10]
    
    ws5 = wb.create_sheet('Top 10 Cuentas')
    ws5.append(['Account ID', 'Total'])
    for row in top_10:
        ws5.append([row['Account ID'], row['Total']])
    
    # Gráfica 3: Bar chart - Top 10 cuentas
    bar = BarChart()
    bar.type = "col"
    bar.title = "Top 10 Cuentas con Mayor Ingreso Neto"
    bar.y_axis.title = "Total (USD)"
    bar.x_axis.title = "Account ID"
    labels3 = Reference(ws5, min_col=1, min_row=2, max_row=ws5.max_row)
    data3 = Reference(ws5, min_col=2, min_row=1, max_row=ws5.max_row)
    bar.add_data(data3, titles_from_data=True)
    bar.set_categories(labels3)
    ws5.add_chart(bar, "D2")
    
    output_xls = base_path / "analisis_graficas.xlsx"
    wb.save(output_xls)
    
    print(f"✓ XLS con gráficas generado: {output_xls}")
    
except ImportError:
    print("⚠ openpyxl no disponible, instalando...")
    import subprocess
    subprocess.run([__import__('sys').executable, '-m', 'pip', 'install', 'openpyxl', '--break-system-packages', '-q'], check=False)
    print("  Intenta ejecutar el script nuevamente")

print("\n✅ Análisis completado exitosamente")
