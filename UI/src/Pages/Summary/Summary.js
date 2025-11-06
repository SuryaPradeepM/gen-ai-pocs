import { useState, useEffect, useContext } from 'react';
import html2pdf from 'html2pdf.js';
import { Scrollbars } from 'react-custom-scrollbars';
import { withStyles } from '@mui/styles';
import { Grid, Typography, Button, TextField, Snackbar, ListItem, List, ListItemText, Alert, Tooltip } from "@mui/material";
import { LoadingButton } from '@mui/lab';
import summaryStyles from "./SummaryStyle";
import * as Commonapirequest from '../../Utils/Commonapirequest/Commonapirequest';
import { Home } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import genaiContext from '../../Context/genai-context';

function Summary(props) {
    const { classes } = props;
    const { setHeading } = useContext(genaiContext);
    const [fileName, setFileName] = useState('');
    const [snackBar, setSnackBar] = useState({ open: false, vertical: 'top', horizontal: 'right', });
    const [fileWithPath, setFileWithPath] = useState(null);
    const navigate = useNavigate()
    const [documentClassificationLoader, setDocumentClassificationLoader] = useState(false);
    const [validatepdfBtn, setvalidatepdfBtn] = useState(true);
    const [documentClassificationResponseData, setDocumentClassificationResponseData] = useState(``);
    const [errorMsgText, setErrorMsgText] = useState('');
    const [classifiedInputValue, setClassifiedInputValue] = useState(`Create a concise summary. The document might contain complex medical information and terminology.
    Make sure that all pertinent and important information is preserved in the summary.
    Breakdown the information into topics and ensure that the summary is accessible and informative, but accurate.`);
    const { vertical, horizontal, open } = snackBar;

    useEffect(() => {
        setHeading('SummarizeDocument')
    }, [])

    const handleDocumentChange = (event) => {
        const { files } = event.target;
        if (files && files.length > 0) {
            // Get the first selected file
            const selectedFile = files[0];
            // Extract the file name
            const fileNameWithoutPath = selectedFile.name;
            // Set the file name for display
            setFileName(fileNameWithoutPath);
            // Set the complete file with path for sending to backend
            setFileWithPath(selectedFile);
        }
    };

    const handleSubmitDocumentClassification = async () => {
        setDocumentClassificationLoader(true);
        setDocumentClassificationResponseData('');
        setErrorMsgText('');
        setvalidatepdfBtn(true);
        const formData = new FormData();
        formData.append('file', fileWithPath);
        let obj = {
            url: `${process.env.REACT_APP_MEETING_SUMMERY_ENDPOINT}summarize_file?prompt=${classifiedInputValue}`,
            data: formData,
            requestMethod: 'POST',
        }
        let getDocClassificationInfo = await Commonapirequest.makeApiRequest(obj);
        if (getDocClassificationInfo && getDocClassificationInfo.status === 200) {
            setDocumentClassificationResponseData(getDocClassificationInfo.data.summary);
            setDocumentClassificationLoader(false);
            setvalidatepdfBtn(false);
        } else {
            setErrorMsgText((getDocClassificationInfo && getDocClassificationInfo.status === 1101) ? 'Response Timeout' : getDocClassificationInfo.data.detail)
            setDocumentClassificationResponseData(null);
            setSnackBar({ ...snackBar, open: true });
            setDocumentClassificationLoader(false);
            setvalidatepdfBtn(true);
        }
    }

    const handleSnackClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setSnackBar({ ...snackBar, open: false });
    };

    const handleChangeClassificationText = (event) => {
        setClassifiedInputValue(event.target.value);
    }

    const downloadPDF = () => {
        const contentElement = document.createElement('div');
        contentElement.style.padding = '20px';
        // Add title to the content
        const titleElement = document.createElement('h1');
        titleElement.textContent = 'Summery using GPT4 (Experiment)';
        contentElement.appendChild(titleElement);

        // Add spacing
        contentElement.appendChild(document.createElement('br'));
        contentElement.appendChild(document.createElement('br'));

        // Add content to the HTML element
        const contentDiv = document.createElement('div');
        contentDiv.innerHTML = documentClassificationResponseData;
        contentElement.appendChild(contentDiv);

        // Convert the HTML content to a PDF
        html2pdf()
            .from(contentElement)
            .save('Summery using GPT4 (Experiment).pdf');
    };

    return (
        <Grid item className={classes.mainSection}>
            <Scrollbars>
                <Snackbar
                    anchorOrigin={{ vertical, horizontal }}
                    open={open}
                    onClose={handleSnackClose}
                    key={vertical + horizontal}
                    autoHideDuration={5000}
                >
                    <Alert
                        onClose={handleSnackClose}
                        severity="error"
                        variant="filled"
                        sx={{ width: '100%' }}
                    >
                        {errorMsgText}
                    </Alert>
                </Snackbar>
                <Grid item className={classes.mainContent}>
                    <Typography className={classes.mainTitle} variant='h1' component={'h1'}><Home onClick={() => { navigate('/') }} className={classes.homeIcon} /> Document Summarization using GPT 4 (Experiment) </Typography>
                    <Grid container spacing={0}>
                        <Grid item xs={4}>
                            <Grid item className={classes.attachedBlock}>
                                <Typography className={classes.inputTitle}>Input</Typography>
                                <Grid item className={classes.attachedTop}>
                                    <Grid item className={classes.labelBox}>
                                        <Typography variant='body1'>Attach Input PDF document<sup>*</sup></Typography>
                                    </Grid>
                                    <Grid item className={classes.checkBoxBlock}>
                                        <Tooltip title="Maximum document size is 1MB" placement="bottom">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
                                                <path fillRule="evenodd" clipRule="evenodd" d="M8 15.1111C11.9274 15.1111 15.1111 11.9274 15.1111 8C15.1111 4.07264 11.9274 0.888889 8 0.888889C4.07264 0.888889 0.888889 4.07264 0.888889 8C0.888889 11.9274 4.07264 15.1111 8 15.1111ZM16 8C16 12.4183 12.4183 16 8 16C3.58172 16 0 12.4183 0 8C0 3.58172 3.58172 0 8 0C12.4183 0 16 3.58172 16 8Z" fill="#1C2B52" />
                                                <path fillRule="evenodd" clipRule="evenodd" d="M7.55469 11.5568V6.22266H8.44358V11.5568H7.55469Z" fill="#1C2B52" />
                                                <path fillRule="evenodd" clipRule="evenodd" d="M7.55469 5.33402V4.44434H8.44358V5.33402H7.55469Z" fill="#1C2B52" />
                                            </svg>
                                        </Tooltip>
                                    </Grid>
                                </Grid>
                                <Grid item className={classes.fieldParent}>
                                    <TextField
                                        id="outlined-multiline-static"
                                        multiline
                                        rows={1}
                                        placeholder="Select the Document"
                                        fullWidth
                                        disabled
                                        className={classes.formtitletextarea}
                                        value={fileName}
                                    />

                                    <Button
                                        className={classes.documentUpload}
                                        component="label"
                                        role={undefined}
                                        variant="contained"
                                        tabIndex={-1}
                                        disableRipple
                                    >
                                        <Grid item className='attachedIcon'></Grid>
                                        Attach
                                        <TextField
                                            type={'file'}
                                            placeholder="Attach"
                                            onChange={handleDocumentChange}
                                            fullWidth
                                            className={classes.documentUploadInput}
                                            disableRipple
                                            inputProps={{ accept: '.pdf' }}
                                        />
                                    </Button>
                                </Grid>
                                <Grid item className={classes.fieldParentTextfiled}>
                                    <Grid item className={classes.labelBox}>
                                        <Typography variant='body1'>Summarization Prompt<sup>*</sup></Typography>
                                    </Grid>
                                    <TextField
                                        id="outlined-multiline-static"
                                        multiline
                                        rows={6}
                                        placeholder="Enter the text here"
                                        value={classifiedInputValue}
                                        onChange={(e) => handleChangeClassificationText(e)}
                                        fullWidth
                                        className={classes.formtitletextarea}
                                    />
                                </Grid>
                            </Grid>
                            <Grid item className={classes.formBlock}>
                                <Grid container spacing={2} className={classes.formDropWrapper}>
                                </Grid>
                                <LoadingButton disableRipple loadingPosition='start' loading={documentClassificationLoader} variant="outlined" disabled={!fileName || documentClassificationLoader || !classifiedInputValue} className={classes.initiateBtn} onClick={handleSubmitDocumentClassification}>
                                    {documentClassificationLoader ? 'Initiating...' : 'Summarize'}
                                </LoadingButton>
                            </Grid>
                            <Grid item className={classes.noteSec}>
                                <Grid item className={classes.noteTop}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <g clipPath="url(#clip0_3_577)">
                                            <path d="M8 0C6.41775 0 4.87104 0.469192 3.55544 1.34824C2.23985 2.22729 1.21447 3.47672 0.608967 4.93853C0.00346629 6.40034 -0.15496 8.00887 0.153721 9.56072C0.462403 11.1126 1.22433 12.538 2.34315 13.6569C3.46197 14.7757 4.88743 15.5376 6.43928 15.8463C7.99113 16.155 9.59966 15.9965 11.0615 15.391C12.5233 14.7855 13.7727 13.7602 14.6518 12.4446C15.5308 11.129 16 9.58225 16 8C15.9977 5.87897 15.1541 3.84547 13.6543 2.34568C12.1545 0.845886 10.121 0.00229405 8 0V0ZM8 14.6667C6.68146 14.6667 5.39253 14.2757 4.2962 13.5431C3.19987 12.8106 2.34539 11.7694 1.84081 10.5512C1.33622 9.33305 1.2042 7.99261 1.46144 6.6994C1.71867 5.40619 2.35361 4.21831 3.28596 3.28596C4.21831 2.35361 5.4062 1.71867 6.6994 1.46143C7.99261 1.2042 9.33305 1.33622 10.5512 1.8408C11.7694 2.34539 12.8106 3.19987 13.5431 4.2962C14.2757 5.39253 14.6667 6.68146 14.6667 8C14.6647 9.76752 13.9617 11.4621 12.7119 12.7119C11.4621 13.9617 9.76752 14.6647 8 14.6667Z" fill="#1C2B52" fillOpacity="0.72" />
                                            <path d="M8.47816 3.37498C8.09371 3.30493 7.69857 3.32023 7.32069 3.4198C6.94281 3.51938 6.59143 3.70078 6.29142 3.95118C5.99141 4.20158 5.7501 4.51486 5.58457 4.86884C5.41903 5.22283 5.33332 5.60887 5.3335 5.99964C5.3335 6.17646 5.40373 6.34602 5.52876 6.47105C5.65378 6.59607 5.82335 6.66631 6.00016 6.66631C6.17697 6.66631 6.34654 6.59607 6.47157 6.47105C6.59659 6.34602 6.66683 6.17646 6.66683 5.99964C6.66666 5.80349 6.70977 5.60972 6.79309 5.43215C6.87641 5.25457 6.99788 5.09757 7.14884 4.97233C7.2998 4.84709 7.47654 4.7567 7.66644 4.70761C7.85635 4.65851 8.05475 4.65193 8.24749 4.68831C8.51085 4.73943 8.75299 4.8679 8.94299 5.0573C9.13299 5.24671 9.26221 5.48845 9.31416 5.75164C9.36662 6.02791 9.3304 6.3137 9.21066 6.56814C9.09092 6.82258 8.89381 7.03265 8.64749 7.16831C8.2396 7.40462 7.90255 7.74599 7.67144 8.15685C7.44034 8.5677 7.32363 9.03302 7.33349 9.50431V9.99964C7.33349 10.1765 7.40373 10.346 7.52875 10.471C7.65378 10.5961 7.82335 10.6663 8.00016 10.6663C8.17697 10.6663 8.34654 10.5961 8.47156 10.471C8.59659 10.346 8.66682 10.1765 8.66682 9.99964V9.50431C8.65846 9.27232 8.71136 9.04222 8.8202 8.83717C8.92904 8.63213 9.08999 8.45938 9.28682 8.33631C9.76983 8.07102 10.1588 7.66262 10.4002 7.16725C10.6416 6.67188 10.7237 6.11388 10.635 5.56999C10.5464 5.02611 10.2914 4.52304 9.90515 4.12997C9.51892 3.73691 9.02041 3.47315 8.47816 3.37498Z" fill="#1C2B52" fillOpacity="0.72" />
                                            <path d="M8.66684 11.9999C8.66684 11.6317 8.36836 11.3333 8.00017 11.3333C7.63197 11.3333 7.3335 11.6317 7.3335 11.9999C7.3335 12.3681 7.63197 12.6666 8.00017 12.6666C8.36836 12.6666 8.66684 12.3681 8.66684 11.9999Z" fill="#1C2B52" fillOpacity="0.72" />
                                        </g>
                                        <defs>
                                            <clipPath id="clip0_3_577">
                                                <rect width="16" height="16" fill="white" />
                                            </clipPath>
                                        </defs>
                                    </svg>
                                    <Typography variant='body1'>Do&apos;s and Dont&apos;s</Typography>
                                </Grid>
                                <Grid item>
                                    <List className={classes.noteList}>
                                        <ListItem>
                                            <ListItemText primary="Upload only .pdf file." />
                                        </ListItem>
                                        <ListItem >
                                            <ListItemText primary="Please don’t upload password protected file" />
                                        </ListItem>
                                        <ListItem >
                                            <ListItemText primary="Please don’t upload file more than 1MB" />
                                        </ListItem>
                                    </List>
                                </Grid>
                            </Grid>
                        </Grid>
                        <Grid item xs={8} className={classes.outputBlock}>
                            <Grid item className={classes.outputTitleBlock}>
                                <Typography className={classes.outputTitle}>Output</Typography>
                                <LoadingButton style={{ margin: 0 }} disableRipple loadingPosition='start' variant="outlined" disabled={validatepdfBtn} className={`${classes.initiateBtn + ' ' + classes.initiatedownloadBtn}`} onClick={downloadPDF}>
                                    Export to PDF
                                </LoadingButton>
                            </Grid>
                            <Grid item className={classes.outputBlockContainer}>
                                <Typography className={classes.outputDescription}>
                                    {documentClassificationResponseData ? documentClassificationResponseData : 'Output will be displayed here...'}
                                </Typography>
                            </Grid>
                        </Grid>
                    </Grid>
                </Grid>
            </Scrollbars>
        </Grid>
    )
}


export default withStyles((theme) => ({
    ...summaryStyles(theme)
}))(Summary);
