import { Box, Button, Grid, IconButton, Paper, Typography } from '@mui/material'
import { useContext, useEffect, useState } from 'react'
import dashboardStyles from './Dashboard.style'
import { withStyles } from '@mui/styles';
import { useNavigate } from 'react-router-dom';
import genaiContext from '../../Context/genai-context';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import { Scrollbars } from 'react-custom-scrollbars-2';
import pocLeftImage from '../../assets/pocLeftImage.svg'
import pocRightImage from '../../assets/pocRightImage.svg'
import dashboardUserImage from '../../assets/dashboardUserImage.svg'

// import VirtualPresenterLogo from '../../assets/VirtualPresenterLogo'
import VirtualPresenterLogo from '../../assets/VirtualPresenterLogo.svg'
import DecisionWizardLogo from '../../assets/DecisionWizardLogo.svg'
import meetingSummariesLogo from '../../assets/meetingSummariesLogo.svg'



import FeviconOuterImage from '../../assets/FeviconOuterImage.svg'
// FeviconOuterImage
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import { CardActionArea } from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import LaunchRoundedIcon from '@mui/icons-material/LaunchRounded';
import { jwtDecode } from "jwt-decode";
import ChatIcon from '@mui/icons-material/Chat';
import PolicyIcon from '@mui/icons-material/Policy';


function Dashboard({ classes }) {
    const navigate = useNavigate()
    const { setHeading } = useContext(genaiContext)
    const [availableServices, setAvailableServices] = useState([])


    useEffect(() => {
        setHeading('')
        const token = sessionStorage.getItem('authToken')
        if (token) {
            try {
                const decodedToken = jwtDecode(token)
                if (decodedToken.services) {
                    setAvailableServices(decodedToken.services)
                }
            } catch (error) {
                console.error('Error decoding token:', error)
            }
        }
    }, [])

    const isServiceAvailable = (serviceName) => {
        return availableServices.includes(serviceName)
    }

    const handleScroll = (direction) => {
        const container = document.getElementById("cardContainer");
        // const scrollAmount = container.clientWidth / 4; // Adjust based on the number of cards visible
        const scrollAmount = container.clientWidth; // Adjust based on the number of cards visible

        if (direction === 'left') {
            container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        } else {
            container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
    }

    const apps = [
        // ... existing apps
        {
            title: 'RAG Chatbot',
            description: 'Chat with your documents using AI',
            icon: <ChatIcon />,
            path: '/rag-chatbot',
            color: '#4CAF50', // or any color that matches your theme
        },
    ];

    return (
        <Grid item className={classes.mainSection}>
            <Scrollbars>
                <Box className={classes.mainContainer}>
                    <Box id="discoverPOC" className={classes.discoverPOCContainer}>
                        <Box className={classes.discoverPOCTopContainer}>
                            <Box className={classes.discoverPOCDes}>
                                <Typography className={classes.pocExplorationContentHeading1}>Discover Generative AI Playzone</Typography>
                                <Typography className={classes.pocExplorationContentDes}>{`Explore our collection of Generative AI (PoC, Proof of Concept) Applications, each designed to`}</Typography>
                                <Typography className={classes.pocExplorationContentDes}>{`showcase the capabilities of Gen AI and push the boundaries of what's possible!`}</Typography>
                            </Box>
                            <Grid spacing={2} marginRight={2}>
                                <Button onClick={() => handleScroll('left')} className={classes.scrollButton}>
                                    <ArrowBackIosIcon fontSize='24' />
                                </Button>
                                <Button onClick={() => handleScroll('right')} className={classes.scrollButton}>
                                    <ArrowForwardIosIcon fontSize='24' />
                                </Button>
                            </Grid>
                        </Box>
                        <Box className={classes.cardNavigation}>
                            <Box id="cardContainer" className={classes.discoverPOCCards}>
                                <Card
                                    onClick={() => { isServiceAvailable('virtual_presenter') && navigate('/virtual_presenter') }}
                                    className={`${classes.cardContainer} ${!isServiceAvailable('virtual_presenter') && classes.disabledCard}`}
                                >                                    
                                    <IconButton title='Go To Virtual Presenter' className={classes.gotoPOCBtn} onClick={() => { navigate('/virtual_presenter') }} >
                                        <LaunchRoundedIcon />
                                    </IconButton>
                                    <Box className={classes.cardHead}>
                                        <img src={VirtualPresenterLogo} className={classes.logo} />
                                    </Box>
                                    <Box className={classes.cardBody}>
                                        <Typography className={classes.cardHeading}>Virtual Presenter</Typography>
                                        <Typography className={classes.cardDes} variant="body2" color="text.secondary">
                                            Discover the future of content Presentation with our Virtual Presenter, offering content presentation
                                            .
                                        </Typography>
                                    </Box>
                                </Card>

                                <Card
                                    onClick={() => { isServiceAvailable('meeting_summary') && navigate('/meeting_summary') }}
                                    className={`${classes.cardContainer} ${!isServiceAvailable('meeting_summary') && classes.disabledCard}`}
                                >
                                    <IconButton title='Go To Meeting Summaries' className={classes.gotoPOCBtn} onClick={() => { navigate('/meeting_summary') }} >
                                        <LaunchRoundedIcon />
                                    </IconButton>
                                    <Box className={classes.cardHead}>
                                        <img src={meetingSummariesLogo} className={classes.logo} />
                                    </Box>
                                    <Box className={classes.cardBody}>
                                        <Typography className={classes.cardHeading}>Meeting Summaries</Typography>
                                        <Typography className={classes.cardDes} variant="body2" color="text.secondary">
                                            Introducing an innovative application that compiles detailed meeting minutes, capturing attendance and discussions for comprehensive documentation.
                                        </Typography>
                                    </Box>
                                </Card>

                                <Card
                                    onClick={() => { isServiceAvailable('logo_generator') && navigate('/logo_generator') }}
                                    className={`${classes.cardContainer} ${!isServiceAvailable('logo_generator') && classes.disabledCard}`}
                                >
                                    <IconButton title='Go To Logo Generator' className={classes.gotoPOCBtn} onClick={() => { navigate('/logo_generator') }} >
                                        <LaunchRoundedIcon />
                                    </IconButton>
                                    <Box className={classes.cardHead}>
                                        <img src={DecisionWizardLogo} className={classes.logo} />
                                    </Box>
                                    <Box className={classes.cardBody}>
                                        <Typography className={classes.cardHeading}>Logo Generator</Typography>
                                        <Typography className={classes.cardDes} variant="body2" color="text.secondary">
                                            Create unique and professional logos with our AI-powered Logo Generator, offering customizable designs for your brand identity needs.
                                        </Typography>
                                    </Box>
                                </Card>

                                <Card
                                    onClick={() => { isServiceAvailable('rag_chatbot') && navigate('/rag-chatbot') }}
                                    className={`${classes.cardContainer} ${!isServiceAvailable('rag_chatbot') && classes.disabledCard}`}
                                >
                                    <IconButton 
                                        title='Go To RAG Chatbot' 
                                        className={classes.gotoPOCBtn} 
                                        onClick={() => navigate('/rag-chatbot')}
                                    >
                                        <LaunchRoundedIcon />
                                    </IconButton>
                                    <Box className={classes.cardHead}>
                                        <ChatIcon style={{ fontSize: 50, color: '#0460a9' }} />
                                    </Box>
                                    <Box className={classes.cardBody}>
                                        <Typography className={classes.cardHeading}>
                                            RAG Chatbot
                                        </Typography>
                                        <Typography 
                                            className={classes.cardDes} 
                                            variant="body2" 
                                            color="text.secondary"
                                        >
                                            Chat with your documents using AI-powered RAG technology. Upload PDFs and get intelligent responses based on their content.
                                        </Typography>
                                    </Box>
                                </Card>

                                <Card
                                    onClick={() => { isServiceAvailable('hr_policies_chatbot') && navigate('/hr-policies-chatbot') }}
                                    className={`${classes.cardContainer} ${!isServiceAvailable('hr_policies_chatbot') && classes.disabledCard}`}
                                >
                                    <IconButton 
                                        title='Go To HR Policies Chatbot' 
                                        className={classes.gotoPOCBtn} 
                                        onClick={() => navigate('/hr-policies-chatbot')}
                                    >
                                        <LaunchRoundedIcon />
                                    </IconButton>
                                    <Box className={classes.cardHead}>
                                        <PolicyIcon style={{ fontSize: 50, color: '#0460a9' }} />
                                    </Box>
                                    <Box className={classes.cardBody}>
                                        <Typography className={classes.cardHeading}>
                                            HR Policies Chatbot
                                        </Typography>
                                        <Typography 
                                            className={classes.cardDes} 
                                            variant="body2" 
                                            color="text.secondary"
                                        >
                                            Ask questions about HR policies. Upload policy PDFs and get streamed answers.
                                        </Typography>
                                    </Box>
                                </Card>
                            </Box>
                        </Box>
                    </Box>
                </Box>
            </Scrollbars>
        </Grid>
    )
}

export default withStyles((theme) => ({
    ...dashboardStyles(theme)
}))(Dashboard);