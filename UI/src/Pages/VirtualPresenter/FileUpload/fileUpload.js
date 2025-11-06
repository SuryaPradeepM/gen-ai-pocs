import React, { useState, useContext, useEffect } from "react";
import axios from "axios";
import VoiceConversion from "../VoiceConvertion/voiceConvertion";
import VoiceConversionRealTimeAPI from "../VoiceConvertionRealTimeAPI/voiceConvertionRealTimeAPI";
import TextToSpeech from "../test";
import {
  Container,
  Grid,
  Box,
  Typography,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Button,
  TextField,
  CircularProgress,
  Snackbar,
  Alert,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack
} from "@mui/material";
import CloseIcon from '@mui/icons-material/Close';
import genaiContext from "../../../Context/genai-context";

const voices = ["alloy", "shimmer", "echo"]

const PPTUpload = () => {
  const [selectedLLM, setSelectedLLM] = useState("realtime-gpt");
  const [selectedSTT, setSelectedSTT] = useState("azure");
  const { setHeading } = useContext(genaiContext);
  const [pdfFile, setPdfFile] = useState(null);
  const [uploadError, setUploadError] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [currentSlide, setCurrentSlide] = useState(1);
  const [generatingPDF, setGeneratingPDF] = useState(false);
  const [totalslides, setTotalSlides] = useState()
  const [openPromptDialog, setOpenPromptDialog] = useState(false);
  const [readingPPT, setReadingPPT] = useState(false)
  const [selectedVoice, setSelectedVoice] = useState('alloy')
  const [userPrompt, setUserPrompt] = useState("Your task is to answer questions asked by the user related to any of these slides. Keep conversations shorter and on point. Note strictly that you are a two-way conversational agent.");
  const [systemPrompt, setSystemPrompt] = useState("Role: You are a conversational agent acting as an expert in presenting PowerPoint slides and answering questions about the presentation content. Your name is Saroja.");
  
  useEffect(() => { setHeading("Virtual Presenter"); }, [setHeading]);

  const handleLLMChange = (e) => {
    setSelectedLLM(e.target.value);
  };

  const handleSTTChange = (e) => {
    setSelectedSTT(e.target.value);
  };

  const  handleVoiceChange = (e) => {
    setSelectedVoice(e.target.value)
  }

  const goToNextSlide = (val) => {
    setCurrentSlide(val);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);
    setUploadError("");
    setGeneratingPDF(true);
    let custom_prompts = {
      "system_prompt": systemPrompt,
      "user_prompt": userPrompt
      
    }
const body={ formData,}

if(selectedLLM == 'gpt-4-o'){
  try {  
    const response = await axios.post(`${process.env.REACT_APP_VIRTUAL_PRESENTER_ENDPOINT}/upload_and_initiate?llm_model=${selectedLLM}`,
      formData,custom_prompts);
    if (response.status !== 200) {
      throw new Error(response.status >= 500
        ? "Server error during file upload. Please try again later."
        : "File upload error. Please check the file format and try again.");
    }

    const { session_id, pdf_content, total_slides } = response.data;
    setSessionId(session_id);
    setTotalSlides(total_slides)
    const pdfBlob = new Blob([Uint8Array.from(atob(pdf_content), c => c.charCodeAt(0))], { type: 'application/pdf' });
    const pdfUrl = URL.createObjectURL(pdfBlob);
    setPdfFile(pdfUrl);
    setGeneratingPDF(false);
  } catch (error) {
    console.error('File upload error:', error);
    setUploadError(error.message);
    setGeneratingPDF(false);
  }
}else{ 

  try {  
    const response = await axios.post(`${process.env.REACT_APP_VIRTUAL_PRESENTER_ENDPOINT_REAL_API}/upload_ppt/`,
      formData);
    if (response.status !== 200) {
      throw new Error(response.status >= 500
        ? "Server error during file upload. Please try again later."
        : "File upload error. Please check the file format and try again.");
    }else{
      const { session_id, pdf_content,file_name, total_slides } = response.data;
      setSessionId(session_id);
        setTotalSlides(total_slides)
        const pdfBlob = new Blob([Uint8Array.from(atob(pdf_content), c => c.charCodeAt(0))], { type: 'application/pdf' });
        const pdfUrl = URL.createObjectURL(pdfBlob);
        setPdfFile(pdfUrl);
        setReadingPPT(true)
      const res = await axios.post(`${process.env.REACT_APP_VIRTUAL_PRESENTER_ENDPOINT_REAL_API}/explain_ppt/?file_name=${file_name}&session_id=${session_id}&voice=${selectedVoice}`)
      if(res.status == 200){
        setReadingPPT(false)
      }else{
        throw new Error(res.status >= 500
          ? "Server error during file upload. Please try again later."
          : alert("Something went wrong, please try later!") );
      }
    }

   
  } catch (error) {
    console.error('File upload error:', error);
    setUploadError(error.message);
    setGeneratingPDF(false);
  }

}
  };

  const handleOpenPromptDialog = () => {
    setOpenPromptDialog(true);
  };

  const handleClosePromptDialog = () => {
    setOpenPromptDialog(false);
  };

  return (
    <Container style={{ display: "flex" }}>
      <Grid container spacing={2} padding={2} style={{ width: "75%" }}>
        <Grid item xs={3}>
          <FormControl size="small" fullWidth margin="normal">
            <InputLabel id="Choose LLM">Choose LLM</InputLabel>
            <Select
              label="Choose LLM"
              value={selectedLLM}
              onChange={handleLLMChange}
           
            >
              <MenuItem value="gpt-4-o" >GPT-4-O</MenuItem>
              <MenuItem value="realtime-gpt" >REALTIME GPT</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      
        <Grid item xs={3}>
          <FormControl size="small" fullWidth margin="normal">
            <InputLabel id="Choose STT">Choose STT</InputLabel>
            <Select
              label="Choose STT"
              value={selectedSTT}
              onChange={handleSTTChange}
            >
              <MenuItem value="azure">AZURE</MenuItem>
              <MenuItem value="deepgram" disabled>DEEPGRAM</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        {selectedLLM == 'gpt-4-o' ? 
        <Grid item xs={3}  marginTop={2}>
          <Button variant="outlined" sx={{textTransform:"capitalize"}} onClick={handleOpenPromptDialog}>
            Configure Prompts
          </Button>
        </Grid>
        :
      
        <Grid item xs={3}>
          <FormControl size="small" fullWidth margin="normal">
            <InputLabel id="Choose Voice">Choose Voice</InputLabel>
            <Select
             label="Choose Voice"
             value={selectedVoice}
             onChange={handleVoiceChange}
            >
              {voices.map((eachVoice, ind) =><MenuItem key={ind} value={eachVoice}>{eachVoice}</MenuItem> )}
            </Select>
          </FormControl>
        </Grid>
      }
        <Grid item xs={3}>
          <FormControl fullWidth margin="normal">
            <Button
              variant="contained"
              component="label"
              disabled={!selectedLLM || !selectedSTT}
              sx={{textTransform:"capitalize"}}
            >
              Upload File
              <input
                type="file"
                accept=".ppt, .pptx"
                onChange={handleFileUpload}
                hidden
              />
            </Button>
            {uploadError && <Alert severity="error">{uploadError}</Alert>}
          </FormControl>
        </Grid>
        {pdfFile && (
          <Grid item xs={12}>
            <iframe
              key={currentSlide}
              src={`${pdfFile}#page=${currentSlide.toString()}`}
              width="100%"
              height="624px"
              style={{ border: '1px solid #ccc' }}
              title="Generated PDF"
            ></iframe>
          </Grid>
        )}
        {generatingPDF && (
          <Box style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "100%", marginTop: "60px" }}>
            <CircularProgress />
            <Typography marginTop={"30px"}>{selectedLLM == 'gpt-4-o' ? "Activating virtual presenter for you..." : "Uploading file data..."}</Typography>
          </Box>
        )}
        
      </Grid>

      {/* Voice Conversion Component */}
      {
        selectedLLM == 'gpt-4-o' ? 
        <VoiceConversion goToNextSlide={goToNextSlide} fileUploaded={!!pdfFile} sessionId={sessionId} totalslides={totalslides} />
        :
        <VoiceConversionRealTimeAPI readingPPT={readingPPT} goToNextSlide={goToNextSlide} fileUploaded={!!pdfFile} sessionId={sessionId} totalslides={totalslides} />
      }
     
      {/* Dialog for User/System Prompt */}
      <Dialog open={openPromptDialog} onClose={handleClosePromptDialog} fullWidth maxWidth="sm">
        <DialogTitle>
          Configure Prompts
          <IconButton
            aria-label="close"
            onClick={handleClosePromptDialog}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} marginTop={4}>
            <TextField
              label="User Prompt"
              multiline
              rows={4}
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              fullWidth
              variant="outlined"
              helperText={`${userPrompt.length} characters`}
            />
            <TextField
              label="System Prompt"
              multiline
              rows={4}
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              fullWidth
              variant="outlined"
              helperText={`${systemPrompt.length} characters`}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePromptDialog} color="primary">
            Close
          </Button>
          <Button onClick={handleClosePromptDialog} color="primary" variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default PPTUpload;
