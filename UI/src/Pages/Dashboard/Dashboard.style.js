import frameImage from '../../assets/Frame.svg'

const dashboardStyles = (theme) => ({
    mainSection: {
        position: 'absolute',
        left: 0,
        top: 94,
        bottom: 0,
        right: 0,

    },

    mainContainer: {
        position: 'absolute',
        left: 0,
        top: 0,
        bottom: 0,
        right: 0,
        padding: theme.spacing(5),
        paddingBottom: theme.spacing(8),
        height: "100%",
    },

    pocExploration: {
        position:"relative",
        backgroundColor: "#F8F8F8",
        padding: theme.spacing(0, 7, 0, 7),
        borderRadius: "14px",
        height: "60vh",
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between"
    },

    pocExplorationContent: {
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",

    },
    pocExplorationContentHeading1: {
        fontFamily: "regular",
        fontSize: "24px",
        fontWeight: "700",
        [theme.breakpoints.down('lg')]: {
            fontSize: "22px",
        },
        [theme.breakpoints.down('md')]: {
            fontSize: "20px",
        },
        [theme.breakpoints.down('md')]: {
            fontSize: "18px",
        },
    },
    pocExplorationContentHeading2: {
        fontFamily: "regular",
        fontWeight: "700",
        lineHeight: "64px",
        fontSize: "46px",
        [theme.breakpoints.down('lg')]: {
            fontSize: "38px",
            lineHeight: "46px",
        },
        [theme.breakpoints.down('md')]: {
            fontSize: "32px",
            lineHeight: "42px",

        },
        [theme.breakpoints.down('sm')]: {
            fontSize: "22px",
        },
    },
    pocExplorationContentDes: {
        fontWeight: "400",
        fontSize: "14px",
        [theme.breakpoints.down('lg')]: {
            fontSize: "13px",
        },
        [theme.breakpoints.down('md')]: {
            fontSize: "12px",
        },
        [theme.breakpoints.down('sm')]: {
            fontSize: "10px",
        },
    },
    userImageContainer: { width: "50%", display: "flex", justifyContent: "flex-end", height: "100%", marginTop: "16px", paddingtop: "16px" },
    mainBtnBox: {
        marginTop: theme.spacing(5),
    },
    exploreMoreBtn: {
        textTransform: "capitalize",
        fontSize: "16px",
        borderColor:"#0460A9",
        color:"#0460A9",
        [theme.breakpoints.down('lg')]: {
            fontSize: "14px",
        },
        [theme.breakpoints.down('md')]: {
            fontSize: "12px",
        },
        '&:hover': {
            borderColor:"#0460A9",
        },
    },

    userImage:{ height: "inherit", height:"59vh", position:"absolute", right:56, bottom:0 },

    gotoWorkspacesBtn: {
        textTransform: "capitalize",
        marginRight: theme.spacing(2),
        backgroundColor:"#0460A9",
        fontSize: "16px",
        [theme.breakpoints.down('lg')]: {
            fontSize: "14px",
        },
        [theme.breakpoints.down('md')]: {
            fontSize: "12px",
        },
        '&:hover': {
            backgroundColor: "#0460A9",
        },
    },

    pocBottomImage: {
        position: "absolute",
        bottom: 0,
        width: "55%",
        [theme.breakpoints.down('lg')]: {
            width: "45%"
        },
        [theme.breakpoints.down('md')]: {
            width: "40%"
        },
    },
    pocLeftImage: {
        position: "absolute",
        left: 0,
        top: "40%",
        width: "15%",
        [theme.breakpoints.down('md')]: {
            width: "18%"
        },
    },
    pocRightImage: {
        position: "absolute",
        right: 0,
        top: "5%",
        width: "15%",
        [theme.breakpoints.down('md')]: {
            width: "16%",
            top: "2%",
        },
    },


    qutecontainer: {
        marginTop: theme.spacing(5),
        paddingBottom: theme.spacing(2)
    },

    discoverPOCTopContainer: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",


    },

    pocArrow: {
        width: "42px",
        height: "30px"
    },


    cardHead: {
        backgroundColor: "#EEEEEE",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "boldfamily",
        fontSize: "32px",
        height: "220px",
        transition: "0.2s",
        borderTopLeftRadius: "20px",
        borderTopRightRadius: "20px",
        [theme.breakpoints.down('lg')]: {
            height: "200px",
            fontSize: "26px"
        },
        [theme.breakpoints.down('md')]: {
            height: "160px",
            fontSize: "22px"
        },
        [theme.breakpoints.down('sm')]: {
            height: "120px",
            fontSize: "20px",
        },

    },
    cardBody: {
        borderBottomLeftRadius: "20px",
        borderBottomRightRadius: "20px",
        backgroundColor: "white",
        padding: theme.spacing(1),

        [theme.breakpoints.down('lg')]: {

            padding: theme.spacing(2, 4),
        },
        [theme.breakpoints.down('sm')]: {

            padding: theme.spacing(2),
        },

        // '&:hover': {
        //     backgroundColor: "#297FCA",
        //     color: "white"
        // },
    },

    cardHeading:{
        fontSize:"20px",
        color:"#0460A9",
        fontFamily:"regular",
        marginBottom:"8px",
        fontWeight:"500",
        [theme.breakpoints.down('lg')]: {
            fontSize: "20px",

        },
        [theme.breakpoints.down('md')]: {
            fontSize: "18px",

        },
        [theme.breakpoints.down('sm')]: {
            fontSize: "16px",

        },

    },
    gotoPOCBtn:{
        position:"absolute",
        top:10,
        right:15
    },
    logo:{
        width:"20%"
    },
    

    discoverPOCContainer: {
        marginTop: theme.spacing(5),
        position: 'relative'
    },
    discoverPOCCards: {
        marginTop: theme.spacing(3),
        display: 'flex',
        overflowX: 'auto',
        scrollBehavior: 'smooth',
        paddingBottom: theme.spacing(2),
        '&::-webkit-scrollbar': {
            display: 'none'
        },
        '-ms-overflow-style': 'none',
        'scrollbar-width': 'none',
    },
    cardContainer: {
        width: '24%',
        position:"relative",
        borderRadius: '20px',
        marginRight: theme.spacing(2),
        flexShrink: 0,
        boxShadow: '0px 1px 3px rgba(0, 0, 0, 0.2)',
        border: "1px solid #EEEEEE"
    },
    cardNavigation: {
        display: 'flex',
        alignItems: 'center',
    },
    scrollButton: {
        minWidth: 'auto',
        padding: theme.spacing(1),
        color: "gray",
        borderRadius: '50%',
        // backgroundColor: theme.palette.background.paper,
        // boxShadow: theme.shadows[2],
        '&:hover': {
            // backgroundColor: theme.palette.primary.main,
            // color: theme.palette.common.white,
        },
    },

    cardDes: {
        fontSize: "14px",
        [theme.breakpoints.down('lg')]: {
            fontSize: "13px",

        },
        [theme.breakpoints.down('md')]: {
            fontSize: "12px",

        },
        [theme.breakpoints.down('sm')]: {
            fontSize: "10px",

        },
    },
    quteImage: {
        width: "18%"
    },
    quteCard: {
        position:"relative",
        width: "100%",
        height: "220px",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        borderRadius: "20px",
        marginTop: theme.spacing(3),
        marginBottom: theme.spacing(4),
        '&:hover': {
            backgroundColor: "#297FCA",
            color: "white"
        }
    },
    card: {
        borderRadius: '43px',
        boxShadow: 'none',
        position: 'relative',
        width: "100%"

    },
    cardTitle: {
        fontFamily: 'boldfamily',
    },

    headingCard: {
        height: '30vh',
        backgroundColor: '#fff',
        transition: 'background-color 0.5s ease-in-out',
        borderRadius: '44px',
        padding: '10px 40px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        boxShadow: 'none',

    },

    heading: {
        fontSize: '48px',
        color: '#3A3A3A'
    },

    desc: {
        fontSize: '18px',
        color: '#6A6A6A'
    },

    absoluteContent: {
        position: 'absolute',
        bottom: '30px',
        padding: '0px 35px'
    },

    absoluteContentQute: {
        position: 'absolute',
        bottom: '30px',
        display: "flex",
        justifyContent: "center",
        width: "100%",
        alignItems: "center",
        padding: '0px 35px'
    },

    aboluteHeading: {
        fontSize: '49px',
        color: '#ffff',
        lineHeight: '52px'
    },

    aboluteDesc: {
        fontSize: '18px',
        color: '#ffff'
    },

    navigationIcon: {
        position: 'absolute',
        right: '14px',
        top: '39px'
    },



    sectioncardQute: {
        borderRadius: '43px',
        boxShadow: 'none',
        backgroundColor: '#0460A9',
        transition: 'background-color 0.5s ease-in-out',
        position: 'relative',
        "&:hover": {
            backgroundColor: '#097ce0',
            "& .image": {
                display: 'none'

            }
        }
    },

    sectioncard: {
        borderRadius: '43px',
        boxShadow: 'none',
        backgroundColor: '#fff',
        transition: 'background-color 0.5s ease-in-out',
        position: 'relative',
        "&:hover": {
            backgroundColor: '#000',
            "& .image": {
                display: 'none'

            }
        }
    },


    sectioncardRight: {
        borderRadius: '43px',
        boxShadow: 'none',
        backgroundColor: '#fff',
        transition: 'background-color 0.5s ease-in-out',
        position: 'relative',
        width: "100%",
        backgroundImage: `url(${frameImage})`,
        backgroundSize: "cover",
        backgroundRepeat: "no-repeat",
        "&:hover": {
            backgroundColor: '#000',
            backgroundImage: `url(${""})`,
            "& .image": {
                display: 'none'

            }
        }
    }


});



export default dashboardStyles;