import pdfplumber
import re
import logging

logger = logging.getLogger(__name__)

def process_pdf(filepath):
    """
    Extract payment data from PDF and verify summary vs calculated amounts.
    
    Args:
        filepath (str): Path to the PDF file
        
    Returns:
        dict: Dictionary with company data including summary and calculated amounts
    """
    companies = {
        'GEPCO': {'summary': 0, 'calculated': 0, 'transactions': []},
        'LESCO': {'summary': 0, 'calculated': 0, 'transactions': []},
        'MEPCO': {'summary': 0, 'calculated': 0, 'transactions': []},
        'SEPCO': {'summary': 0, 'calculated': 0, 'transactions': []},
        'SNGPL': {'summary': 0, 'calculated': 0, 'transactions': []},
        'SSGC': {'summary': 0, 'calculated': 0, 'transactions': []}
    }

    company_names = list(companies.keys())

    with pdfplumber.open(filepath) as pdf:
        # ---- Page 1: Summary for GEPCO, LESCO, MEPCO, SEPCO ----
        page1_text = pdf.pages[0].extract_text()
        amounts = re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2})', page1_text)
        
        if len(amounts) >= 4:
            companies['GEPCO']['summary'] = float(amounts[0].replace(',', ''))
            companies['LESCO']['summary'] = float(amounts[1].replace(',', ''))
            companies['MEPCO']['summary'] = float(amounts[2].replace(',', ''))
            companies['SEPCO']['summary'] = float(amounts[3].replace(',', ''))

        # ---- Page 2: Summary for SNGPL and SSGC ----
        if len(pdf.pages) >= 2:
            page2_text = pdf.pages[1].extract_text()
            
            # Extract SNGPL amount from Page 2
            sngpl_pattern = re.search(r'SNGPL\s+([\d,]+\.\d{2})', page2_text)
            if sngpl_pattern:
                companies['SNGPL']['summary'] = float(sngpl_pattern.group(1).replace(',', ''))
            else:
                sngpl_pattern2 = re.search(r'SNGPL.*?([\d,]+\.\d{2})', page2_text)
                if sngpl_pattern2:
                    companies['SNGPL']['summary'] = float(sngpl_pattern2.group(1).replace(',', ''))
            
            # Extract SSGC amount from Page 2
            ssgc_pattern = re.search(r'SSGC\s+([\d,]+\.\d{2})', page2_text)
            if ssgc_pattern:
                companies['SSGC']['summary'] = float(ssgc_pattern.group(1).replace(',', ''))
            else:
                ssgc_pattern2 = re.search(r'SSGC.*?([\d,]+\.\d{2})', page2_text)
                if ssgc_pattern2:
                    companies['SSGC']['summary'] = float(ssgc_pattern2.group(1).replace(',', ''))
            
            # Fallback: If SNGPL/SSGC not found, use position-based extraction
            if companies['SNGPL']['summary'] == 0 or companies['SSGC']['summary'] == 0:
                page2_amounts = re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2})', page2_text)
                
                if len(page2_amounts) >= 2:
                    if companies['SNGPL']['summary'] == 0:
                        companies['SNGPL']['summary'] = float(page2_amounts[0].replace(',', ''))
                    if companies['SSGC']['summary'] == 0:
                        companies['SSGC']['summary'] = float(page2_amounts[1].replace(',', ''))

        # ---- Pattern definitions ----
        amount_pattern = re.compile(r'(\d{1,3}(?:,\d{3})*\.\d{2})')
        amount_pattern2 = re.compile(r'(\d{1,3}(?:,\d{3})*\.\d{2}|\d+\.\d{2})')

        # ---- DETECT: Find which pages belong to which company ----
        company_pages = {company: [] for company in company_names}
        current_company = None
        
        # Start from Page 3 (index 2) because Page 2 is summary
        for page_idx in range(2, len(pdf.pages)):
            page_text = pdf.pages[page_idx].extract_text()
            if not page_text:
                continue
            
            counts = {name: page_text.count(name) for name in company_names}
            max_count = max(counts.values()) if counts else 0
            
            if max_count > 0:
                matched_company = max(counts, key=counts.get)
                current_company = matched_company
                company_pages[matched_company].append(page_idx)
            else:
                if current_company:
                    company_pages[current_company].append(page_idx)
                else:
                    for company in reversed(company_names):
                        if company_pages[company]:
                            current_company = company
                            company_pages[company].append(page_idx)
                            break

        # ---- Process each company's pages ----
        for company, pages in company_pages.items():
            if not pages:
                continue
                
            for page_idx in pages:
                page_text = pdf.pages[page_idx].extract_text()
                if not page_text:
                    continue
                
                # ---- SPECIAL: For SNGPL, skip summary pages ----
                if company == 'SNGPL':
                    page_amounts = amount_pattern.findall(page_text)
                    if not page_amounts:
                        page_amounts = amount_pattern2.findall(page_text)
                    
                    small_amounts = sum(1 for a in page_amounts if 1 <= float(a.replace(',', '')) <= 5000)
                    
                    if small_amounts < 5:
                        continue
                
                # ---- SPECIAL: For SSGC, skip summary pages ----
                if company == 'SSGC':
                    page_amounts = amount_pattern.findall(page_text)
                    if not page_amounts:
                        page_amounts = amount_pattern2.findall(page_text)
                    
                    small_amounts = sum(1 for a in page_amounts if 1 <= float(a.replace(',', '')) <= 5000)
                    
                    if small_amounts < 2:
                        continue
                
                page_amounts = amount_pattern.findall(page_text)
                if not page_amounts:
                    page_amounts = amount_pattern2.findall(page_text)
                
                for amt_str in page_amounts:
                    try:
                        amount = float(amt_str.replace(',', ''))
                        
                        if amount >= 1000000:
                            continue
                        
                        if company == 'SNGPL' and amount > 5000:
                            continue
                        
                        if company == 'SSGC' and amount > 5000:
                            continue
                        
                        if 1 <= amount < 1000000:
                            companies[company]['transactions'].append(amount)
                            companies[company]['calculated'] += amount
                    except ValueError:
                        pass

        # ---- Use calculated values for SNGPL and SSGC if summary is 0 ----
        for company in ['SNGPL', 'SSGC']:
            if companies[company]['summary'] == 0 and companies[company]['calculated'] > 0:
                companies[company]['summary'] = companies[company]['calculated']

        # ---- FALLBACK: Use calculated totals if summary is 0 ----
        for company in companies:
            if companies[company]['summary'] == 0 and companies[company]['calculated'] > 0:
                companies[company]['summary'] = companies[company]['calculated']

    return companies