from django import forms
from django.conf import settings
from cloudinary.forms import CloudinaryFileField
from django.template.loader import render_to_string
import json
import cloudinary

class CloudinaryMediaLibraryWidget(forms.ClearableFileInput):
    """
    Widget that replaces the standard file input with a Cloudinary Media Library button.
    This completely overrides the default file input to use Cloudinary instead.
    """
    class Media:
        js = ['https://media-library.cloudinary.com/global/all.js']
        
    def __init__(self, attrs=None, options=None):
        default_attrs = {'class': 'cloudinary-media-library-hidden'}
        if attrs:
            default_attrs.update(attrs)
        self.options = options or {}
        super().__init__(default_attrs)
    
    def flatatt(self, attrs):
        """Helper function to convert attributes to HTML string format"""
        return ''.join([f' {k}="{v}"' for k, v in attrs.items()])
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
            
        # Hide the original file input but keep it in the DOM for form submission
        attrs['class'] = attrs.get('class', '') + ' cloudinary-media-library-input'
        attrs['style'] = 'display: none;'  # Hide the original file input
        final_attrs = self.build_attrs(attrs)
        
        # Get the original input but hide it
        original_input = super().render(name, value, attrs, renderer)
        
        # Get Cloudinary configuration
        cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', '')
        api_key = settings.CLOUDINARY_STORAGE.get('API_KEY', '')
        
        # Value handling and preview URL setup
        preview_url = ''
        preview_style = 'display: none;'
        
        if value:
            if hasattr(value, 'url'):
                preview_url = value.url
                preview_style = ''
            elif isinstance(value, str):
                # If it's a string (public_id), create the URL
                preview_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/q_auto:best/{value}"
                preview_style = ''
                
        # Generate unique IDs for this widget instance
        widget_id = f"cloudinary_widget_{name}"
        hidden_input_id = f"cloudinary_value_{name}"
        
        # Build HTML for the widget that completely replaces the file input
        html = f'''
        <div class="cloudinary-widget-container" id="{widget_id}_container">
            {original_input}
            <input type="hidden" id="{hidden_input_id}" name="_cloudinary_value_{name}" value="{value or ''}" />
            
            <button type="button" class="button cloudinary-media-library-btn" id="{widget_id}_btn">
                Choose from Cloudinary Library
            </button>
            
            <div class="cloudinary-preview-container" style="margin-top: 10px; max-width: 300px;">
                <img src="{preview_url}" alt="Preview" style="max-width: 100%; max-height: 150px; {preview_style}" 
                    id="{widget_id}_preview" class="cloudinary-preview-image" />
            </div>
        </div>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Disable the Browse button that Django generates
            var fileInput = document.getElementById('id_{name}');
            if (fileInput) {{
                var parentLabel = fileInput.parentElement;
                if (parentLabel && parentLabel.tagName === 'LABEL') {{
                    parentLabel.style.display = 'none';
                }}
                
                // Hide the "Currently:" and "Change:" labels if they exist
                var labels = document.querySelectorAll('label[for="id_{name}"]');
                labels.forEach(function(label) {{
                    if (label.textContent.includes('Currently:') || 
                        label.textContent.includes('Change:') ||
                        label.textContent.includes('Clear')) {{
                        label.style.display = 'none';
                    }}
                }});
                
                // Hide the clear checkbox if it exists
                var clearCheckbox = document.getElementById('id_{name}-clear');
                if (clearCheckbox) {{
                    var clearLabel = clearCheckbox.parentElement;
                    if (clearLabel && clearLabel.tagName === 'LABEL') {{
                        clearLabel.style.display = 'none';
                    }} else {{
                        clearCheckbox.style.display = 'none';
                    }}
                }}
            }}
            
            // Initialize the Cloudinary widget
            function initCloudinaryWidget() {{
                var button = document.getElementById('{widget_id}_btn');
                var hiddenInput = document.getElementById('{hidden_input_id}');
                var fileInput = document.getElementById('id_{name}');
                var preview = document.getElementById('{widget_id}_preview');
                
                if (!button) return;
                
                // Only initialize once
                if (button.getAttribute('data-initialized') === 'true') return;
                button.setAttribute('data-initialized', 'true');
                
                button.addEventListener('click', function(e) {{
                    e.preventDefault();
                    
                    if (typeof cloudinary === 'undefined') {{
                        console.error('Cloudinary library not loaded');
                        alert('Cloudinary Media Library could not be loaded. Please check your internet connection and try again.');
                        return;
                    }}
                    
                    try {{
                        var mediaLibrary = cloudinary.createMediaLibrary(
                            {{
                                cloud_name: '{cloud_name}',
                                api_key: '{api_key}',
                                multiple: false,
                                max_files: 1,
                                folder: {{
                                    resource_type: 'image',
                                    path: '{self.options.get("folder", "")}'
                                }},
                                transformation: {{ quality: 'auto:best', fetch_format: 'auto' }}
                            }},
                            {{
                                insertHandler: function(data) {{
                                    if (data && data.assets && data.assets.length > 0) {{
                                        var selectedAsset = data.assets[0];
                                        var publicId = selectedAsset.public_id;
                                        
                                        // Set the value in the hidden input
                                        if (hiddenInput) hiddenInput.value = publicId;
                                        
                                        // Clear any file in the file input and set its value programmatically
                                        if (fileInput) {{
                                            fileInput.value = '';
                                            // Set a data attribute to store the Cloudinary public_id
                                            fileInput.setAttribute('data-cloudinary-public-id', publicId);
                                        }}
                                        
                                        // Update preview image
                                        if (preview) {{
                                            preview.src = 'https://res.cloudinary.com/{cloud_name}/image/upload/q_auto:best/' + publicId;
                                            preview.style.display = 'block';
                                        }}
                                        
                                        // Trigger change event
                                        if (fileInput) {{
                                            fileInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                        }}
                                    }}
                                }}
                            }}
                        );
                        
                        mediaLibrary.show();
                    }} catch (error) {{
                        console.error('Error initializing Cloudinary Media Library:', error);
                        alert('Error initializing Cloudinary Media Library: ' + error.message);
                    }}
                }});
            }}
            
            // Try to initialize immediately and also wait for script to load
            if (typeof cloudinary !== 'undefined') {{
                initCloudinaryWidget();
            }} else {{
                // Set a check interval to initialize once cloudinary is loaded
                var checkInterval = setInterval(function() {{
                    if (typeof cloudinary !== 'undefined') {{
                        clearInterval(checkInterval);
                        initCloudinaryWidget();
                    }}
                }}, 100);
                
                // Fallback to ensure we don't wait forever
                setTimeout(function() {{
                    clearInterval(checkInterval);
                }}, 10000);
                
                // Try to load the script again if it hasn't loaded
                var script = document.createElement('script');
                script.src = 'https://media-library.cloudinary.com/global/all.js';
                document.head.appendChild(script);
            }}
        }});
        </script>
        
        <style>
            .cloudinary-widget-container {{
                margin: 10px 0;
            }}
            .cloudinary-media-library-btn {{
                background: #447e9b;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
            }}
            .cloudinary-media-library-btn:hover {{
                background: #366b7c;
            }}
            .cloudinary-media-library-input {{
                display: none !important;
            }}
        </style>
        '''
        return html

class CloudinaryMediaLibraryField(CloudinaryFileField):
    """Custom form field that uses the Cloudinary Media Library widget"""
    def __init__(self, *args, **kwargs):
        # Extract any options for the widget
        widget_kwargs = {}
        options = None
        if 'options' in kwargs:
            options = kwargs.pop('options')
            widget_kwargs['options'] = options
        
        # Initialize the field with our custom widget
        super().__init__(*args, **kwargs)
        self.widget = CloudinaryMediaLibraryWidget(attrs=widget_kwargs, options=options)
        
    def clean(self, value, initial=None):
        """
        Custom clean method to handle both regular file uploads and
        Cloudinary public_id values from our widget
        """
        # Check if we have a value from the hidden Cloudinary input
        if isinstance(value, dict) and 'data-cloudinary-public-id' in value:
            # Return the public_id directly
            return value['data-cloudinary-public-id']
        
        # Otherwise delegate to parent class
        return super().clean(value, initial)
