import { useState, useContext, useEffect } from 'react';
import { withStyles } from '@mui/styles';
import {
    Grid,
    Typography,
    TextField,
    Button,
    Chip,
    MenuItem,
    FormControl,
    InputLabel,
    Select,
    Box,
    Alert,
    CircularProgress,
} from '@mui/material';
import { Home } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { Scrollbars } from 'react-custom-scrollbars-2';
import logoGeneratorStyles from './LogoGenerator.style';
import genaiContext from '../../Context/genai-context';

const INITIAL_FORM_STATE = {
    brand_name: '',
    slogan: '',
    style: 'minimal',
    color_scheme: 'monochrome',
    industry: '',
    target_audience: '',
    usage_context: 'all_purpose',
    preferred_symbols: [],
    avoid_elements: [],
    brand_values: [],
    competitor_differentiation: '',
    additional_notes: '',
    font_style: 'sans-serif',
    maintain_simplicity: true,
};

const STYLE_OPTIONS = ['minimal', 'modern', 'classic', 'playful', 'luxurious'];
const COLOR_SCHEMES = ['monochrome', 'complementary', 'analogous', 'triadic'];
const FONT_STYLES = ['sans-serif', 'serif', 'modern', 'decorative', 'handwritten'];

function LogoGenerator({ classes }) {
    const navigate = useNavigate();
    const { setHeading } = useContext(genaiContext);
    const [formData, setFormData] = useState(INITIAL_FORM_STATE);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [logoData, setLogoData] = useState(null);
    const [currentChipInput, setCurrentChipInput] = useState({
        preferred_symbols: '',
        avoid_elements: '',
        brand_values: '',
    });

    useEffect(() => {
        setHeading('Logo Generator');
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleChipInputChange = (e, field) => {
        setCurrentChipInput((prev) => ({
            ...prev,
            [field]: e.target.value,
        }));
    };

    const handleAddChip = (field) => {
        if (currentChipInput[field].trim()) {
            setFormData((prev) => ({
                ...prev,
                [field]: [...prev[field], currentChipInput[field].trim()],
            }));
            setCurrentChipInput((prev) => ({
                ...prev,
                [field]: '',
            }));
        }
    };

    const handleDeleteChip = (field, index) => {
        setFormData((prev) => ({
            ...prev,
            [field]: prev[field].filter((_, i) => i !== index),
        }));
    };

    const prepareFormData = () => {
        return {
            ...formData,
            preferred_symbols: formData.preferred_symbols.filter(item => item.trim()),
            avoid_elements: formData.avoid_elements.filter(item => item.trim()),
            brand_values: formData.brand_values.filter(item => item.trim()),
            brand_name: formData.brand_name.trim(),
            slogan: formData.slogan.trim(),
            industry: formData.industry.trim(),
            target_audience: formData.target_audience.trim(),
            competitor_differentiation: formData.competitor_differentiation.trim(),
            additional_notes: formData.additional_notes.trim(),
        };
    };

    const handleSubmit = async () => {
        if (!validateForm()) {
            return;
        }
        
        setLoading(true);
        setError('');
        try {
            const cleanedFormData = prepareFormData();
            const response = await fetch(`${process.env.REACT_APP_LOGO_GENERATOR_ENDPOINT}/api/v1/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(cleanedFormData),
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to generate logo');
            }

            setLogoData(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async () => {
        if (!logoData?.logo_url) return;
        
        try {
            const response = await fetch(`${process.env.REACT_APP_LOGO_GENERATOR_ENDPOINT}${logoData.logo_url}`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${formData.brand_name}_logo.png`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            setError('Failed to download logo');
        }
    };

    const validateForm = () => {
        if (!formData.brand_name.trim()) {
            setError('Brand name is required');
            return false;
        }
        
        if (!formData.industry.trim()) {
            setError('Industry is required');
            return false;
        }

        if (!formData.target_audience.trim()) {
            setError('Target audience is required');
            return false;
        }

        return true;
    };

    return (
        <Grid item className={classes.mainSection}>
            <Scrollbars>
                <Grid item className={classes.mainContent}>
                    <Typography className={classes.mainTitle}>
                        <Home onClick={() => navigate('/')} className={classes.homeIcon} />
                        Logo Generator
                    </Typography>

                    <Box className={classes.formContainer}>
                        <Box className={classes.inputSection}>
                            <Typography className={classes.sectionTitle}>Input Parameters</Typography>
                            
                            <TextField
                                fullWidth
                                label="Brand Name"
                                name="brand_name"
                                value={formData.brand_name}
                                onChange={handleInputChange}
                                className={classes.formField}
                                required
                            />

                            <TextField
                                fullWidth
                                label="Slogan"
                                name="slogan"
                                value={formData.slogan}
                                onChange={handleInputChange}
                                className={classes.formField}
                            />

                            <FormControl fullWidth className={classes.formField}>
                                <InputLabel>Style</InputLabel>
                                <Select
                                    name="style"
                                    value={formData.style}
                                    onChange={handleInputChange}
                                    label="Style"
                                >
                                    {STYLE_OPTIONS.map((style) => (
                                        <MenuItem key={style} value={style}>
                                            {style.charAt(0).toUpperCase() + style.slice(1)}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            <FormControl fullWidth className={classes.formField}>
                                <InputLabel>Color Scheme</InputLabel>
                                <Select
                                    name="color_scheme"
                                    value={formData.color_scheme}
                                    onChange={handleInputChange}
                                    label="Color Scheme"
                                >
                                    {COLOR_SCHEMES.map((scheme) => (
                                        <MenuItem key={scheme} value={scheme}>
                                            {scheme.charAt(0).toUpperCase() + scheme.slice(1)}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            <TextField
                                fullWidth
                                label="Industry"
                                name="industry"
                                value={formData.industry}
                                onChange={handleInputChange}
                                className={classes.formField}
                            />

                            <TextField
                                fullWidth
                                label="Target Audience"
                                name="target_audience"
                                value={formData.target_audience}
                                onChange={handleInputChange}
                                className={classes.formField}
                            />

                            {/* Chip Input Fields */}
                            {['preferred_symbols', 'avoid_elements', 'brand_values'].map((field) => (
                                <Box key={field} className={classes.formField}>
                                    <TextField
                                        fullWidth
                                        label={field.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                                        value={currentChipInput[field]}
                                        onChange={(e) => handleChipInputChange(e, field)}
                                        onKeyPress={(e) => {
                                            if (e.key === 'Enter') {
                                                e.preventDefault();
                                                handleAddChip(field);
                                            }
                                        }}
                                    />
                                    <Box className={classes.chipContainer}>
                                        {formData[field].map((item, index) => (
                                            <Chip
                                                key={index}
                                                label={item}
                                                onDelete={() => handleDeleteChip(field, index)}
                                            />
                                        ))}
                                    </Box>
                                </Box>
                            ))}

                            <Button
                                variant="contained"
                                className={classes.generateButton}
                                onClick={handleSubmit}
                                disabled={loading || !formData.brand_name}
                                fullWidth
                            >
                                {loading ? <CircularProgress size={24} color="inherit" /> : 'Generate Logo'}
                            </Button>
                        </Box>

                        <Box className={classes.outputSection}>
                            <Typography className={classes.sectionTitle}>Generated Logo</Typography>
                            
                            {error && (
                                <Alert severity="error" className={classes.errorMessage}>
                                    {error}
                                </Alert>
                            )}

                            {logoData && (
                                <Box className={classes.previewContainer}>
                                    <img
                                        src={`${process.env.REACT_APP_LOGO_GENERATOR_ENDPOINT}${logoData.preview_url}`}
                                        alt="Generated Logo Preview"
                                        className={classes.logoPreview}
                                    />
                                    <Button
                                        variant="contained"
                                        onClick={handleDownload}
                                        className={classes.downloadButton}
                                    >
                                        Download Logo
                                    </Button>
                                </Box>
                            )}

                            {!logoData && !error && !loading && (
                                <Typography align="center" color="textSecondary">
                                    Your generated logo will appear here
                                </Typography>
                            )}
                        </Box>
                    </Box>
                </Grid>
            </Scrollbars>
        </Grid>
    );
}

export default withStyles((theme) => ({
    ...logoGeneratorStyles(theme)
}))(LogoGenerator); 