import hawkeyeLogo from "../../assets/logo.png";
const headerStyles = (theme) => ({
  headerSection: {
    borderRadius: 0,
    boxShadow: "none",
    // background: '#50E2D0',
    borderBottom: "1px solid #e3e3e3",
    // height: 72,
    display: "flex",
    alignItems: "center",
    position: "relative",
    zIndex: 5,
    [theme.breakpoints.down("md")]: {
      height: 68,
    },
  },
  headerBlock: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: theme.spacing(2, 4),
    height: "auto",
    opacity: 1,
    transform: "translateY(0)",
    transition:
      "height 0.3s ease-in-out, opacity 0.3s ease-in-out, transform 0.3s ease-in-out",
    overflow: "hidden",
  },

  headerBlockHidden: {
    height: 0,
    opacity: 0,
    transform: "translateY(-100%)",
    transition:
      "height 0.3s ease-in-out, opacity 0.3s ease-in-out, transform 0.3s ease-in-out",
    overflow: "hidden",
  },
  logoParent: {
    display: "flex",
    alignItems: "center",
  },
  logo: {
    width: 155,
    height: 25,
    backgroundImage: `url(${hawkeyeLogo})`,
    backgroundSize: "cover",
    backgroundRepeat: "no-repeat",
    backgroundPosition: "center",
    // [theme.breakpoints.down('md')]: {
    //     width: 110,
    //     height: 34,
    // },
    cursor: "pointer",
  },
  tabsParent: {
    display: "flex",
    justifyContent: "center",
  },
  userParent: {
    display: "flex",
    alignItems: "center",
  },
  userProfile: {
    display: "flex",
    alignItems: "center",
    "& .MuiAvatar-root": {
      width: 40,
      height: 40,
      [theme.breakpoints.down("lg")]: {
        width: 36,
        height: 36,
      },
      [theme.breakpoints.down("md")]: {
        width: 32,
        height: 32,
      },
    },
    "& h3": {
      fontSize: 14,
      fontFamily: "regular",
      color: "#2C4177",
      fontWeight: 700,
      paddingLeft: theme.spacing(1),
      [theme.breakpoints.down("md")]: {
        fontSize: 12,
      },
    },
  },
  warningmsg: {
    backgroundColor: "#0460A9",
    position: "absolute",
    color: "#fff",
    fontSize: 12,
    fontFamily: "regular",
    width: "100vw",
    top: 68,
    left: 0,
    right: 0,
    padding: theme.spacing(0.5),
    textAlign: "center",
  },
  warningmsg2: {
    top: 0,
  },
  historyIcon: {
    marginRight: theme.spacing(2),
  },
  docLogoTitle: {
    fontFamily: "boldfamily",
    fontSize: 22,
    alignItems: "center",
    paddingLeft: theme.spacing(2),
    paddingTop: theme.spacing(1.5),
    position: "relative",
    "& sup": {
      fontFamily: "regular",
      color: "red",
      fontSize: 12,
      paddingLeft: theme.spacing(0.5),
    },
    "&::after": {
      content: '""',
      left: 8,
      top: 8,
      bottom: 0,
      width: 1,
      margin: "auto",
      height: "70%",
      position: "absolute",
      backgroundColor: "#777",
    },
  },
  workspaceNavContainer: {
    position: "absolute",
    top: 0,
    left: "35%",
    textAlign: "center",
  },

  openNavBar: {
    padding: theme.spacing(1.5, 1),
    position: "relative",
    transition: "all 0.4s ease-in-out", // Smooth transition
    borderBottomLeftRadius: "18px",
    borderBottomRightRadius: "18px",
    backgroundColor: "#F5F5F5",
    border: "none",
    display: "flex",
    justifyContent: "space-around",
    alignItems: "center",
    width: "28vw",
    // paddingBottom: theme.spacing(2),
    boxShadow: "0px 2px 12px -8px rgba(0,0,0,0.75)",
  },

  navbarController: {
    width: "60%",
    borderRadius: "24px",
    borderBottom: "2px solid #AFAFAF",
    // marginBottom: '10px',
    cursor: "pointer",
    [theme.breakpoints.down("lg")]: {
      width: "50%",
    },
    [theme.breakpoints.down("md")]: {
      width: "50%",
    },
  },
  openConroler: {
    left: "38%",
    width: "102px",
  },
  closeNavBar: {
    position: "absolute",
    top: 0,
    left: "47%",
    transform: "translateX(-50%)",
    width: "40%",
    height: "26px",
    borderBottomLeftRadius: "18px",
    borderBottomRightRadius: "18px",
    backgroundColor: "#F5F5F5",
    border: "none",
    boxShadow: "0px 4px 12px -8px rgba(0,0,0,0.75)",
    textAlign: "center",
    transition: "all 0.4s ease-in-out", // Smooth transition,
    [theme.breakpoints.down("lg")]: {
      height: "22px",
      width: "40%",
      left: "50%",
      borderBottomLeftRadius: "15px",
      borderBottomRightRadius: "15px",
    },
    [theme.breakpoints.down("md")]: {
      height: "18px",
      width: "40%",
      borderBottomLeftRadius: "12px",
      borderBottomRightRadius: "12px",
    },
  },

  navItem: {
    display: "flex",
    alignItems: "center",
    cursor: "pointer",
    // marginLeft:theme.spacing(3)
  },

  screenNumber: {
    height: "28px",
    width: "28px",
    fontSize: "16px",
    border: "1px solid #0460A9",
    // textAlign:"center",
    borderRadius: "50%",
    fontFamily: "medium",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    [theme.breakpoints.down("lg")]: {
      height: "26px",
      width: "26px",
      fontSize: "14px",
    },
    [theme.breakpoints.down("md")]: {
      height: "22px",
      width: "22px",
      fontSize: "14px",
    },
  },
  screenName: {
    fontSize: "16px",
    marginLeft: "6px",
    [theme.breakpoints.down("lg")]: {
      fontSize: "14px",
    },
    [theme.breakpoints.down("md")]: {
      fontSize: "14px",
    },
  },
});
export default headerStyles;
