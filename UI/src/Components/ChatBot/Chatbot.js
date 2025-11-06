import React, { useState, useRef, useEffect, useContext } from "react";
import {
  Paper,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  Menu,
  MenuItem,
  Drawer,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import { withStyles } from "@mui/styles";
import chatbotStyles from "./Chtbot.style";
import axios from "axios";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import { useParams } from "react-router-dom";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import genaiContext from "../../Context/genai-context";
import ContentCopyRoundedIcon from "@mui/icons-material/ContentCopyRounded";

const options = ["Workspace", "PubMed"];
const Chatbot = ({
  open,
  onClose,
  classes,
  template,
  workspaceName,
  setUpdateSectionListFlag,
}) => {
  const [messages, setMessages] = useState([]);
  const [pubMedMsgs, setPubMedMsgs] = useState([]);
  const [displayMsgs, setDisplayMsgs] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const messageListRef = useRef(null);
  const [filterAnchorEl, setFilterAnchorEl] = useState(null);
  const [value, setValue] = useState(options[0]);
  const [selectedFilter, setSelectedFilter] = useState("Workspace");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [sectionTitle, setSectionTitle] = useState("");
  const [currentMessage, setCurrentMessage] = useState(null);
  const [addedResponses, setAddedResponses] = useState([]);
  const [addedPubmedResponses, setAddedPubmedResponses] = useState([]);
  const [currentMsgIndex, setCurrentMsgIndex] = useState(null);
  const { id } = useParams();
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    scrollToBottom();
  }, [messages, pubMedMsgs, displayMsgs]);

  useEffect(() => {
    if (selectedFilter === "Workspace") {
      setDisplayMsgs([...messages]);
    } else {
      setDisplayMsgs([...pubMedMsgs]);
    }
  }, [selectedFilter, messages, pubMedMsgs]);

  const scrollToBottom = () => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  };

  const handleFilter = (event) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSendMessage = () => {
    if (inputValue.trim() === "") return;

    if (selectedFilter === "Workspace") {
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: inputValue, sender: "user" },
      ]);
    } else {
      setPubMedMsgs((prevMessages) => [
        ...prevMessages,
        { text: inputValue, sender: "user" },
      ]);
    }

    setInputValue("");

    axios
      .post(`${process.env.REACT_APP_COMPENDIUM_ENDPOINT}api/v1/chat`, {
        source: selectedFilter.toLowerCase(),
        query: inputValue,
        workspace_name: workspaceName,
      })
      .then((response) => {
        if (selectedFilter === "Workspace") {
          setMessages((prevData) => [
            ...prevData,
            { sender: "bot", text: response.data.answer },
          ]);
        } else {
          setPubMedMsgs((prevData) => [
            ...prevData,
            { sender: "bot", text: response.data.answer },
          ]);
        }
      })
      .catch((error) => {
        console.error(error);
        setTimeout(() => {
          alert(error?.message + ", Try again later!");
        }, 1000);
      });
  };

  const handleDialogOpen = (message, index) => {
    setCurrentMessage(message);
    setDialogOpen(true);
    setCurrentMsgIndex(index);
  };

  const handleCopy = (message, index) => {
    navigator.clipboard.writeText(message).then(() => {
      setCopied(true);
      setCurrentMsgIndex(index);
      setTimeout(() => setCopied(false), 5000);
    });
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
    setSectionTitle("");
  };

  const handleDialogSave = () => {
    let source;
    if (selectedFilter === "Workspace") {
      source = [selectedFilter + " : " + messages[currentMsgIndex - 1].text];
    } else {
      source = [selectedFilter + " : " + pubMedMsgs[currentMsgIndex - 1].text];
    }
    axios
      .post(
        `${process.env.REACT_APP_COMPENDIUM_ENDPOINT}api/v1/${id}/section-headers`,
        {
          heading: sectionTitle,
          bot_response: true,
          response: currentMessage.text,
          sources: source,
        },
      )
      .then((response) => {
        if (selectedFilter === "Workspace") {
          setAddedResponses((prevState) => [...prevState, currentMsgIndex]);
        } else {
          setAddedPubmedResponses((prevState) => [
            ...prevState,
            currentMsgIndex,
          ]);
        }

        handleDialogClose();
        setUpdateSectionListFlag(true);
      })
      .catch((error) => {
        console.error(error);
        handleDialogClose();
        setTimeout(() => {
          alert("Something went wrong, Try again later!");
        }, 1000);
      });
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{ style: { width: "33%" } }}
    >
      <Box className={classes.chatHeader}>
        <Box className={classes.QuteFevicon} style={{ padding: "4px" }}></Box>
      </Box>
      <List
        ref={messageListRef}
        sx={{
          height: `70%`,
          width: "100%",
          overflowY: "auto",
          paddingRight: "16px",
          borderRadius: "4px",
          "&::-webkit-scrollbar": {
            width: "8px",
          },
          "&": {
            scrollbarWidth: "thin",
          },
        }}
        className={classes.messageSection}
      >
        {displayMsgs?.map((message, index) => (
          <ListItem
            key={index}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: `${message.sender === "bot" ? "flex-start" : "flex-end"}`,
            }}
          >
            <Paper
              elevation={message.sender === "bot" ? 0 : 1}
              style={{
                backgroundColor: `${message.sender === "bot" ? "#D1EAFE" : "white"}`,
              }}
              className={classes.messageText}
            >
              {message.text}
            </Paper>
            {template == "Meeting Summaries"
              ? message.sender === "bot" && (
                  <Button
                    startIcon={<ContentCopyRoundedIcon />}
                    className={classes.addToPlayground}
                    variant="contained"
                    disabled={
                      selectedFilter == "Workspace"
                        ? addedResponses?.includes(index)
                        : addedPubmedResponses?.includes(index)
                    }
                    onClick={() => handleCopy(message.text, index)}
                  >
                    {copied && index === currentMsgIndex ? "Copied" : "Copy"} to
                    Clipboard
                  </Button>
                )
              : message.sender === "bot" && (
                  <Button
                    startIcon={<AddOutlinedIcon />}
                    className={classes.addToPlayground}
                    variant="contained"
                    disabled={
                      selectedFilter == "Workspace"
                        ? addedResponses?.includes(index)
                        : addedPubmedResponses?.includes(index)
                    }
                    onClick={() => handleDialogOpen(message, index)}
                  >
                    Add to Playground
                  </Button>
                )}
            <Box>
              {message.sender === "bot" ? (
                <Box className={classes.botInfo}>
                  {/* <Typography className={classes.you}>PIN</Typography>
                                        <Typography style={{ marginLeft: "40px", marginTop: "7px", fontSize: "13px" }}> <strong>Source:</strong> Document name (title), Page 02</Typography> */}
                </Box>
              ) : (
                <Typography className={classes.you}>You</Typography>
              )}
            </Box>
          </ListItem>
        ))}
      </List>
      <Box className={classes.inputsection}>
        <div>
          <Button
            variant="contained"
            className={classes.allDropdown}
            onClick={handleFilter}
            disableRipple
            endIcon={<KeyboardArrowDownIcon />}
          >
            {selectedFilter}
          </Button>
          <Menu
            id="simple-all-menu"
            anchorEl={filterAnchorEl}
            keepMounted
            open={Boolean(filterAnchorEl)}
            onClose={handleFilterClose}
            value={selectedFilter}
          >
            {options.map((option, addIndex) => (
              <MenuItem
                key={option}
                onClick={(e) => {
                  setSelectedFilter(option);
                  handleFilterClose();
                }}
              >
                {option}
              </MenuItem>
            ))}
          </Menu>
        </div>
        <TextField
          value={inputValue}
          onChange={handleInputChange}
          fullWidth
          variant="outlined"
          placeholder="Ask me anything! I’m here to help"
          className={classes.inputField}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              handleSendMessage();
            }
          }}
        />
      </Box>
      <Dialog
        className={classes.addSecDialog}
        open={dialogOpen}
        onClose={handleDialogClose}
      >
        <DialogTitle className={classes.dialogHeadText}>
          Add Section
        </DialogTitle>
        <DialogContent>
          <Typography className={classes.secTitle}>Section Title</Typography>
          <TextField
            autoFocus
            margin="dense"
            label="Section Title"
            fullWidth
            size="small"
            value={sectionTitle}
            onChange={(e) => setSectionTitle(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleDialogClose}
            className={classes.btnText}
            variant="outlined"
            color="primary"
          >
            Close
          </Button>
          <Button
            disabled={!sectionTitle}
            onClick={handleDialogSave}
            className={classes.btnText}
            variant="contained"
            color="primary"
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Drawer>
  );
};

export default withStyles((theme) => ({
  ...chatbotStyles(theme),
}))(Chatbot);
