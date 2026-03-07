"""
File Upload Field Detector
Detects and catalogs file upload inputs with sample file references
"""
from typing import List, Dict
from playwright.async_api import Page
from pathlib import Path
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class FileUploadDetector:
    """Detects file upload fields and prepares test data"""
    
    def __init__(self):
        self.sample_files = {
            'image': ['test_image.jpg', 'test_image.png'],
            'document': ['test_document.pdf', 'test_document.docx'],
            'spreadsheet': ['test_data.csv', 'test_data.xlsx'],
            'any': ['test_file.txt']
        }
        
        # Create sample files directory if needed
        self.samples_dir = Path('data/test_files')
        self.samples_dir.mkdir(parents=True, exist_ok=True)
        self._create_sample_files()
    
    def _create_sample_files(self):
        """Create dummy test files for upload testing"""
        try:
            # Create a small text file
            (self.samples_dir / 'test_file.txt').write_text('Sample test file content for upload testing')
            
            # Create a small CSV
            (self.samples_dir / 'test_data.csv').write_text('name,value,category\ntest1,123,A\ntest2,456,B')
            
            # Create a small image placeholder (1x1 PNG)
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
            (self.samples_dir / 'test_image.png').write_bytes(png_data)
            
            logger.debug(f"✅ Test files available in {self.samples_dir}")
        except Exception as e:
            logger.warning(f"⚠️  Could not create test files: {e}")
    
    async def detect_file_inputs(self, page: Page) -> List[Dict]:
        """
        Detect all file upload inputs on page
        
        Returns:
            List of file input metadata with test file recommendations
        """
        js_code = """
        () => {
            const fileInputs = [];
            
            document.querySelectorAll('input[type="file"]').forEach((input, index) => {
                // Find label
                let label = '';
                if (input.labels && input.labels[0]) {
                    label = input.labels[0].textContent.trim();
                } else {
                    // Look for nearby label
                    const parent = input.closest('div, label, fieldset');
                    if (parent) {
                        const labelEl = parent.querySelector('label');
                        if (labelEl) label = labelEl.textContent.trim();
                    }
                }
                
                const accept = input.getAttribute('accept') || '';
                const multiple = input.hasAttribute('multiple');
                const required = input.hasAttribute('required');
                const isVisible = input.offsetParent !== null || 
                                 window.getComputedStyle(input).display !== 'none';
                
                fileInputs.push({
                    index: index,
                    name: input.name || `file_${index}`,
                    id: input.id || '',
                    label: label,
                    accept: accept,
                    multiple: multiple,
                    required: required,
                    visible: isVisible,
                    selector: input.id ? `#${input.id}` : `input[type="file"]:nth-of-type(${index + 1})`
                });
            });
            
            return fileInputs;
        }
        """
        
        try:
            file_inputs = await page.evaluate(js_code)
            
            # Enhance with test file recommendations
            for inp in file_inputs:
                inp['recommended_files'] = self._get_recommended_files(inp['accept'])
                inp['test_data_type'] = 'file_upload'
                inp['test_file_path'] = str(self.samples_dir / inp['recommended_files'][0]) if inp['recommended_files'] else None
            
            if file_inputs:
                logger.info(f"📎 Found {len(file_inputs)} file upload field(s)")
            
            return file_inputs
        except Exception as e:
            logger.error(f"File input detection error: {e}")
            return []
    
    def _get_recommended_files(self, accept_attr: str) -> List[str]:
        """Get recommended test files based on accept attribute"""
        if not accept_attr:
            return self.sample_files['any']
        
        accept_lower = accept_attr.lower()
        
        if 'image' in accept_lower or any(ext in accept_lower for ext in ['.jpg', '.png', '.gif']):
            return self.sample_files['image']
        elif 'pdf' in accept_lower or 'document' in accept_lower:
            return self.sample_files['document']
        elif 'csv' in accept_lower or 'spreadsheet' in accept_lower or '.xlsx' in accept_lower:
            return self.sample_files['spreadsheet']
        else:
            return self.sample_files['any']
