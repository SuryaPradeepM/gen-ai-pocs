import attachedIcon from "../../assets/attached_icon.svg";
const summaryStyles = (theme) => ({
  mainSection: {
    position: "absolute",
    left: 0,
    top: 94,
    bottom: 0,
    right: 0,
  },
  mainContent: {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    right: 0,
    padding: theme.spacing(6, 14),
    [theme.breakpoints.down("lg")]: {
      padding: theme.spacing(8, 12),
    },
    [theme.breakpoints.down("md")]: {
      padding: theme.spacing(6, 6),
    },
  },
  mainTitle: {
    color: "#1C2B52",
    fontFamily: "boldfamily",
    fontSize: 34,
    paddingBottom: theme.spacing(2),
    display: "flex",
    alignItems: "center",
    [theme.breakpoints.down("lg")]: {
      fontSize: 30,
    },

    [theme.breakpoints.down("md")]: {
      fontSize: 26,
    },
  },
  textclassificationBlock: {
    position: "relative",
    display: "flex",
    alignItems: "center",
    marginTop: theme.spacing(1),
  },
  textclassificationDrop: {
    borderRadius: "4px",
    background: "linear-gradient(90deg, #1C2B52 0%, #385294 100%)",
    padding: theme.spacing(2.3, 4),
    display: "flex",
    alignItems: "center",
    [theme.breakpoints.down("md")]: {
      flexBasis: "25.833333%",
      width: "25.833333%",
      maxWidth: "25.833333%",
    },
    [theme.breakpoints.down("sm")]: {
      flexBasis: "32.833333%",
      width: "32.833333%",
      maxWidth: "32.833333%",
    },
    "& p": {
      color: "#FFF",
      fontSize: 14,
      paddingLeft: theme.spacing(1.5),
      fontFamily: "regular",
      [theme.breakpoints.down("lg")]: {
        fontSize: 12,
      },
    },
  },
  analyzeParent: {
    display: "flex",
    alignItems: "center",
    marginLeft: theme.spacing(4),
  },
  analyzeText: {
    color: "#1C2B52",
    fontSize: 14,
    [theme.breakpoints.down("lg")]: {
      fontSize: 12,
    },
  },
  attachedBlock: {
    position: "relative",
    padding: theme.spacing(2, 0),
  },
  attachedTop: {
    display: "flex",
    justifyContent: "space-between",
  },
  labelBox: {
    display: "flex",
    alignItems: "center",
    position: "relative",
    "& svg": {
      marginRight: theme.spacing(1),
    },
    "& p": {
      color: "#1C2B52",
      fontSize: 14,
      fontFamily: "regular",
      [theme.breakpoints.down("lg")]: {
        fontSize: 12,
      },
      "& sup": {
        color: "red",
      },
    },
  },
  checkBoxBlock: {
    position: "relative",
  },
  checkBoxLabel: {
    position: "relative",
    "& span": {
      fontSize: 14,
      [theme.breakpoints.down("lg")]: {
        fontSize: 12,
      },
    },
  },
  fieldParent: {
    position: "relative",
  },
  fieldParentTextfiled: {
    position: "relative",
    width: "100%",
    marginTop: theme.spacing(3),
  },
  formtitletextarea: {
    position: "relative",
    opacity: "0.99",
    // background: '#DBF3F0',
    borderRadius: "0px",
    fontSize: 14,
    [theme.breakpoints.down("lg")]: {
      fontSize: 12,
    },
    "& textarea": {
      fontSize: 14,
      [theme.breakpoints.down("lg")]: {
        fontSize: 12,
      },
    },
    "& fieldset": {
      borderColor: "none",
      border: "1px solid #e3e3e3",
      borderRadius: "0px",
      "&::hover": {
        borderColor: "none",
      },
    },
  },
  documentUpload: {
    right: 14,
    position: "absolute",
    padding: theme.spacing(0, 5),
    paddingLeft: theme.spacing(7),
    fontSize: 14,
    boxShadow: "none !important",
    borderRadius: 0,
    textTransform: "capitalize",
    margin: "auto",
    top: 0,
    bottom: 0,
    height: 40,
    cursor: "pointer",
    pointerEvents: "auto",
    [theme.breakpoints.down("lg")]: {
      fontSize: 12,
    },
    "& .attachedIcon": {
      width: 20,
      height: 20,
      position: "absolute",
      left: 30,
      top: 0,
      bottom: 0,
      margin: "auto",
      backgroundImage: `url(${attachedIcon})`,
      backgroundSize: "14px",
      backgroundRepeat: "no-repeat",
      backgroundPosition: "center",
    },
  },
  documentUploadInput: {
    position: "absolute",
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
    opacity: 0,
    zIndex: 1,
    cursor: "pointer",
    pointerEvents: "auto",
    "& fieldset": {
      cursor: "pointer",
      pointerEvents: "auto",
    },
  },
  formBlock: {
    position: "relative",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "end",
  },
  formDropWrapper: {
    display: "flex",
    alignItems: "center",
    width: "60%",
  },
  formRow: {
    position: "relative",
  },
  formLabelText: {
    color: "#1C2B52",
    fontSize: 14,
    fontFamily: "regular",
    paddingBottom: theme.spacing(0.5),
    [theme.breakpoints.down("lg")]: {
      fontSize: 12,
    },
  },
  autocompleteDrop: {
    position: "relative",
    width: "100%",
    background: "#dbf3f0",
    "& .MuiInputBase-root": {
      borderRadius: "0px",
    },
    "& fieldset": {
      border: "1px solid #50E2D0",
    },
    "& input": {
      fontSize: 14,
      [theme.breakpoints.down("lg")]: {
        fontSize: 12,
      },
    },

    "& .MuiInputBase-sizeSmall": {
      paddingTop: theme.spacing(1) + "!important",
      paddingBottom: theme.spacing(1) + "!important",
    },
  },
  initiateBtn: {
    position: "relative",
    borderRadius: "10px",
    background: "#1C2B52",
    border: "none",
    color: "#FFF",
    fontSize: 14,
    padding: theme.spacing(1, 6),
    height: 40,
    textTransform: "capitalize",
    [theme.breakpoints.down("lg")]: {
      fontSize: 12,
    },
    "&:hover": {
      border: "none",
      background: "#1C2B52",
      color: "#FFF",
    },
    "&.Mui-disabled": {
      background: "rgb(28 43 82 / 41%)",
      border: "none",
      color: "#FFF",
      cursor: "not-allowed",
      pointerEvents: "auto",
    },
  },
  noteSec: {
    position: "relative",
    marginTop: theme.spacing(5),
  },
  noteTop: {
    display: "flex",
    alignItems: "center",
    position: "relative",
    "& svg": {
      marginRight: theme.spacing(1),
    },
    "& p": {
      color: "rgba(28, 43, 82, 0.72)",
      fontSize: 14,
      fontWeight: "bold",
      [theme.breakpoints.down("lg")]: {
        fontSize: 12,
      },
    },
  },
  noteList: {
    position: "relative",
    marginLeft: theme.spacing(1),
    "& li": {
      position: "relative",
      padding: 0,
      margin: 0,
      paddingLeft: theme.spacing(1.5),
      "&::before": {
        content: '""',
        position: "absolute",
        left: 0,
        top: 0,
        bottom: 0,
        width: 3,
        height: 3,
        borderRadius: "100%",
        backgroundColor: "rgba(28, 43, 82, 0.72)",
        margin: "auto",
      },
      "& .MuiListItemText-root": {
        margin: 0,
        padding: 0,
      },
      "& span": {
        fontFamily: "regular",
        fontSize: 14,
        [theme.breakpoints.down("lg")]: {
          fontSize: 12,
        },
      },
    },
  },
  outputBlock: {
    padding: theme.spacing(0, 0, 0, 4),
    position: "relative",
    "&::after": {
      content: "''",
      position: "absolute",
      top: 0,
      bottom: 0,
      left: 38,
      width: 1,
      background: "#e3e3e3",
      height: "80%",
      margin: "auto",
    },
  },
  outputTitleBlock: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: theme.spacing(0, 0, 0, 6),
  },
  outputBlockContainer: {
    padding: theme.spacing(4),
    border: "1px solid #e3e3e3",
    borderRadius: "16px",
    margin: theme.spacing(2, 0, 2, 6),
  },
  outputTitle: {
    fontFamily: "boldfamily",
    fontSize: 20,
  },
  inputTitle: {
    fontFamily: "boldfamily",
    fontSize: 20,
    padding: theme.spacing(0, 0, 3, 0),
  },
  outputDescription: {},
  initiatedownloadBtn: {
    margin: theme.spacing(0, 2),
    float: "right",
  },
  homeIcon: {
    height: "30px",
    width: "30px",
    cursor: "pointer",
    marginRight: "10px",
  },
});

export default summaryStyles;
