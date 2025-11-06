import QFevicon from "../../assets/QFevicon.svg";
const chatbotStyles = (theme) => ({
  chatHeader: {
    borderBottom: "1px solid #ccc",
    padding: "16px",
    // textAlign: 'center',
    paddingTop: theme.spacing(5),
    fontFamily: "boldfamily",
    fontSize: "20px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    width: "100%",
  },
  allDropdown: {
    padding: theme.spacing(1.5),
  },
  botIcon: {
    marginRight: "12px",
    marginBottom: "4px",
    height: "28px",
    width: "28px",
  },
  heading: {
    fontFamily: "boldfamily",
    fontSize: "20px",
    marginLeft: "4px",
    marginTop: "10px",
  },
  messageSection: {
    overflowY: "auto",

    padding: "16px",
  },

  inputsection: {
    position: "absolute",
    bottom: 0,
    width: "100%",
    display: "flex",
    alignItems: "center",
    borderTop: "1px solid #ccc",
    padding: theme.spacing(4),
    zIndex: "10",
  },
  QuteFevicon: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    width: "39px",
    height: "39px",
    backgroundImage: `url('${QFevicon}')`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
  },
  addToPlayground: {
    textTransform: "capitalize",
    backgroundColor: "#F4F4F4",
    padding: theme.spacing(0.7, 2),
    color: "black",
    borderRadius: "54px",
    border: "none",
    cursor: "pointer",
    marginTop: theme.spacing(1),
    "&:hover": {
      backgroundColor: "#F4F4F4",
      color: "black",
    },
  },
  btnText: {
    textTransform: "capitalize",
  },
  addSecDialog: {
    "& .MuiDialog-paper": {
      minWidth: "40vw",
      padding: theme.spacing(2),
    },
  },
  messageText: {
    padding: theme.spacing(1, 2),
    fontFamily: "medium",
    fontSize: "14px",
    fontWeight: 500,
    display: "flex",
    alignItems: "flex-end",
  },
  botInfo: {
    display: "flex",
  },

  you: {
    color: "#0460A9",
    fontSize: "15px",
    marginTop: "7px",
    fontFamily: "boldfamily",
    fontWeight: "600",
  },

  inputField: {
    "& .MuiOutlinedInput-root": {
      height: "47px", // Adjust the overall height
      "& input": {
        height: "40px", // Adjust the height of the input field
        padding: "10px 14px", // Adjust padding to center the text vertically
      },
    },
  },

  sendButton: {
    height: "45px",
    width: "50px",
    marginLeft: "20px",
  },
  dialogHeadText: {
    textAlign: "center",
    color: "#0460A9",
    fontFamily: "medium",
  },
  secTitle: {
    marginBottom: theme.spacing(1),
    color: "black",
    fontWeight: "600",
  },
});

export default chatbotStyles;
