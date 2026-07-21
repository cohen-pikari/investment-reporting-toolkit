import pandas as pd
import sqlite3
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

def generate_formatted_excel():
    # 🌟 UPGRADE: Querying the relational database warehouse layer directly via SQL
    db_path = "data/portfolio_warehouse.db"
    conn = sqlite3.connect(db_path)
    
    query = """
        SELECT 
            ticker AS [Ticker],
            security_name AS [Security Name],
            market_value AS [Internal MV ($)]
        FROM internal_ledger
    """
    df_internal = pd.read_sql_query(query, conn)
    conn.close()
    
    # Simulate matching custodian external truth values
    custodian_mv_map = {
        'AAPL': 326590.00,
        'BHP.AX': 290058.00,
        'ALT-VC-PRV': 475000.00
    }
    
    # Reconstruct the tracking sheets logic on top of database outputs
    df_internal['Custodian MV ($)'] = df_internal['Ticker'].map(custodian_mv_map)
    df_internal['Net Variance ($)'] = df_internal['Custodian MV ($)'] - df_internal['Internal MV ($)']
    
    def classify_exception(row):
        if abs(row['Net Variance ($)']) > 0.01:
            return 'ALTERNATIVES_VALUATION_LAG' if 'ALT' in row['Ticker'] else 'PRICING_BREAK'
        return 'NONE'
        
    df_internal['Exception Type'] = df_internal.apply(classify_exception, axis=1)
    
    # Execute identical layout formatting matrices
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Daily Exception Summary"
    ws.views.sheetView.showGridLines = True
    
    font_title = Font(name='Calibri', size=16, bold=True, color='1F497D')
    font_header = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    font_data = Font(name='Calibri', size=11, bold=False)
    font_total = Font(name='Calibri', size=11, bold=True, color='1F497D')
    
    fill_header = PatternFill(start_color='1F497D', end_color='1F497D', fill_type='solid')
    fill_break = PatternFill(start_color='F2DCDB', end_color='F2DCDB', fill_type='solid')
    fill_lag = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
    
    align_center = Alignment(horizontal='center', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    
    thin_side = Side(border_style="thin", color="D9D9D9")
    double_side = Side(border_style="double", color="1F497D")
    
    border_cell = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    border_total = Border(top=thin_side, bottom=double_side)
    
    ws['A1'] = "INVESTMENT OPERATIONS DAILY MIS BREAKSHEET"
    ws['A1'].font = font_title
    ws['A2'] = f"Report Date: {datetime.today().strftime('%Y-%m-%d')} | Source: SQL Database Layer"
    ws['A2'].font = Font(name='Calibri', size=11, italic=True, color='595959')
    
    headers = list(df_internal.columns)
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_num, value=header)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = border_cell
        
    for row_idx, row_data in enumerate(df_internal.values, 5):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = font_data
            cell.border = border_cell
            
            if col_idx in:
                cell.alignment = align_center
            elif col_idx in:
                cell.alignment = align_right
                cell.number_format = '$#,##0.00'
            else:
                cell.alignment = align_left
                
            if row_data[5] == 'PRICING_BREAK' and col_idx in:
                cell.fill = fill_break
            elif row_data[5] == 'ALTERNATIVES_VALUATION_LAG' and col_idx in:
                cell.fill = fill_lag

    total_row = len(df_internal) + 5
    ws.cell(row=total_row, column=1, value="Total Exposure").font = font_total
    ws.cell(row=total_row, column=1).border = border_total
    
    for c in range(2, 7):
        ws.cell(row=total_row, column=c).border = border_total
        
    calc_cell = ws.cell(row=total_row, column=5, value=f"=SUM(E5:E{total_row-1})")
    calc_cell.font = font_total
    calc_cell.alignment = align_right
    calc_cell.number_format = '$#,##0.00'
    
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col.column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
        
    wb.save("output/portfolio_exception_sheet.xlsx")
    print("📊 Formatted Spreadsheet successfully compiled directly from production SQL extraction parameters.")

if __name__ == "__main__":
    generate_formatted_excel()

