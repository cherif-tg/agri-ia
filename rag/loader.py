"""
File loading module for RAG
Supports CSV, PDF, and Excel files
"""

import pandas as pd
import pdfplumber
from pathlib import Path
import logging
from typing import Union, Optional, Dict

logger = logging.getLogger(__name__)


class FileLoader:
    """Load various file formats"""
    
    ALLOWED_EXTENSIONS = {'.csv', '.pdf', '.xlsx', '.xls'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
    
    @staticmethod
    def validate_file(file_path: Union[str, Path]) -> bool:
        """Validate file before loading"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() not in FileLoader.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported format: {path.suffix}")
        
        if path.stat().st_size > FileLoader.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {path.stat().st_size}")
        
        return True
    
    @staticmethod
    def load_csv(file_path: Union[str, Path], encoding: str = 'utf-8') -> pd.DataFrame:
        """Load CSV file"""
        
        logger.info(f"Loading CSV: {file_path}")
        
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"✓ CSV: {len(df)} rows, {len(df.columns)} columns")
            return df
        except UnicodeDecodeError:
            for enc in ['latin-1', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, encoding=enc)
                    logger.info(f"✓ CSV loaded with encoding {enc}")
                    return df
                except:
                    continue
            raise ValueError("Unable to decode CSV")
    
    @staticmethod
    def load_pdf(file_path: Union[str, Path]) -> pd.DataFrame:
        """Extract tables from PDF"""
        
        logger.info(f"Loading PDF: {file_path}")
        all_tables = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                logger.info(f"PDF: {len(pdf.pages)} pages")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()
                    
                    if tables:
                        for table in tables:
                            if len(table) > 1:
                                df = pd.DataFrame(table[1:], columns=table[0])
                                all_tables.append(df)
                                logger.info(f"  Page {page_num}: Found table")
            
            if not all_tables:
                logger.warning("⚠️ No tables found in PDF")
                return pd.DataFrame()
            
            df_combined = pd.concat(all_tables, ignore_index=True)
            logger.info(f"✓ PDF: {len(df_combined)} rows extracted")
            return df_combined
            
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise
    
    @staticmethod
    def load_excel(file_path: Union[str, Path], sheet_name: int = 0) -> pd.DataFrame:
        """Load Excel file"""
        
        logger.info(f"Loading Excel: {file_path}")
        
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"✓ Excel: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"Excel error: {e}")
            raise
    
    @staticmethod
    def load_file(file_path: Union[str, Path]) -> pd.DataFrame:
        """Load any supported file format"""
        
        FileLoader.validate_file(file_path)
        
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.csv':
            return FileLoader.load_csv(file_path)
        elif extension == '.pdf':
            return FileLoader.load_pdf(file_path)
        elif extension in ['.xlsx', '.xls']:
            return FileLoader.load_excel(file_path)
        else:
            raise ValueError(f"Unsupported format: {extension}")
    
    @staticmethod
    def get_file_info(df: pd.DataFrame) -> Dict:
        """Get info about loaded data"""
        
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
            'missing_values': df.isnull().sum().to_dict()
        }
