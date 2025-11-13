import { withStyles } from "@mui/styles";
import headerStyles from "./Header.style";
import {
  Grid,
  Avatar,
  Typography,
  Button,
  Fade,
  Box,
  IconButton,
} from "@mui/material";
import { useContext, useEffect, useState } from "react";
import genaiContext from "../../Context/genai-context";
import { useNavigate, useLocation } from "react-router-dom";
import HistoryIcon from "@mui/icons-material/History";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";

function Header(props) {
  const { classes } = props;
  const navigate = useNavigate();
  let path = useLocation();
  const {
    heading,
    setIsUploadTemplate,
    setHeaderAvailable,
    setHeading,
    workspaceScreenNumber,
    setWorkspaceScreenNumber,
    workspaceId,
  } = useContext(genaiContext);
  const [quteHeaderOpened, setQuteHeaderOpened] = useState(true);
  const [show, setShow] = useState(false);

  const showNav = () => {
    setShow(true);
  };
  var timeoutID = null;
  const hideNav = () => {
    timeoutID = setTimeout(() => {
      setShow(false);
    }, 2000);
  };

  const stayNav = () => {
    clearTimeout(timeoutID);
  };

  useEffect(() => {
    if (
      (heading === "Qute" && path.pathname !== "/Qute") ||
      heading == "Virtual Presenter"
    ) {
      closeQuteHeder();
    } else {
      openQuteHeader();
    }
  }, [path.pathname, heading]);

  const handleFileUpload = () => {
    navigate("Qute/Playground");
    setIsUploadTemplate(true);
  };

  const openQuteHeader = () => {
    setQuteHeaderOpened(true);
    setHeaderAvailable(true);
  };

  const closeQuteHeder = () => {
    setTimeout(() => {
      setQuteHeaderOpened(false);
      setHeaderAvailable(false);
    }, 1500);
  };

  const handleWorkspaceScreen = (screenNum) => {
    setWorkspaceScreenNumber(screenNum);
    switch (screenNum) {
      case 1:
        navigate(`/workspaces/${workspaceId}`);
        break;
      case 2:
        navigate(`/workspaces/workspaceview/${workspaceId}`);
        break;
      case 3:
        navigate(`/workspaces/workspaceview/${workspaceId}/report/`);
        break;
      default:
        navigate(`/workspaces/${workspaceId}`);
        break;
    }
  };

  return (
    <>
      {quteHeaderOpened ? (
        <Grid
          container
          onMouseLeave={() => {
            ((heading == "Qute" && path.pathname != "/Qute") ||
              heading == "Virtual Presenter") &&
              closeQuteHeder();
          }}
          className={classes.headerSection}
        >
          <Grid
            onMouseEnter={() => {
              ((heading == "Qute" && path.pathname != "/Qute") ||
                heading == "Virtual Presenter") &&
                openQuteHeader();
            }}
            container
            spacing={0}
            className={`${classes.headerBlock} ${quteHeaderOpened ? "" : classes.headerBlockHidden}`}
          >
            <Grid item className={classes.logoParent}>
              <Grid
                item
                className={classes.logo}
                onClick={() => {
                  navigate("/");
                  setHeading("");
                  setWorkspaceScreenNumber(0);
                }}
              ></Grid>
              {heading && (
                <Typography
                  className={classes.docLogoTitle}
                  onClick={() => {
                    navigate("/");
                    setHeading("");
                    setWorkspaceScreenNumber(0);
                  }}
                  style={{ cursor: "pointer" }}
                >
                  {heading}
                  <sup>alpha</sup>
                </Typography>
              )}
            </Grid>
            {/* Center title: dynamic based on `heading`, defaults to GenAI Playzone */}
            <Grid item className={classes.centerTitle}>
              <Box
                className={classes.playzoneWrapper}
                onMouseEnter={() => {
                  (heading == "Qute" || heading == "Virtual Presenter") &&
                    openQuteHeader();
                }}
              >
                <Typography
                  className={classes.playzoneTitle}
                  onClick={() => {
                    navigate("/");
                    setHeading("");
                    setWorkspaceScreenNumber(0);
                  }}
                  style={{ cursor: "pointer" }}
                >
                  {heading ? heading : "GenAI PlayZone"}
                </Typography>
                {/* Playful halo and orbiting particle elements (animated on hover) */}
                <span className={classes.playzoneHalo} />
                <span className={classes.playzoneParticles}>
                  <span className={classes.playParticle} />
                  <span className={classes.playParticle2} />
                  <span className={classes.playParticle3} />
                </span>
              </Box>
            </Grid>
            {heading == "Workspaces" && workspaceScreenNumber != 0 && (
              <Box
                className={classes.workspaceNavContainer}
                onMouseEnter={stayNav}
                onMouseLeave={hideNav}
              >
                <Fade in={show}>
                  <Box className={classes.openNavBar}>
                    {["Input", "Chunk Explorer", "Playground"].map(
                      (screenName, index) => (
                        <Box
                          className={classes.navItem}
                          onClick={() => {
                            handleWorkspaceScreen(index + 1);
                          }}
                        >
                          <Typography
                            style={{
                              backgroundColor: `${workspaceScreenNumber == index + 1 ? "black" : ""}`,
                              color: `${workspaceScreenNumber == index + 1 ? "white" : "#0460A9"}`,
                              border: `${workspaceScreenNumber == index + 1 ? "1px solid black" : "1px solid #0460A9"}`,
                            }}
                            className={classes.screenNumber}
                          >
                            {index + 1}
                          </Typography>
                          <Typography
                            style={{
                              color: `${workspaceScreenNumber == index + 1 ? "black" : "#0460A9"}`,
                              textDecoration: `${workspaceScreenNumber == index + 1 ? "" : "underline"}`,
                              fontFamily: `${workspaceScreenNumber == index + 1 ? "boldFamily" : "regular"}`,
                            }}
                            className={classes.screenName}
                          >
                            {screenName}
                          </Typography>
                        </Box>
                      ),
                    )}
                  </Box>
                </Fade>
                {!show && (
                  <Box
                    onMouseEnter={showNav}
                    className={classes.closeNavBar}
                    style={{
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    <Fade in={!show}>
                      <Box className={classes.navbarController} />
                    </Fade>
                  </Box>
                )}
              </Box>
            )}
            <Grid item className={classes.userParent}>
              <Grid className={classes.userProfile}>
                {heading == "Workspaces" && (
                  <IconButton title="Activity" className={classes.historyIcon}>
                    <HistoryIcon
                      onClick={() => {
                        navigate("/workspaces/history");
                        setWorkspaceScreenNumber(0);
                      }}
                    />
                  </IconButton>
                )}
                {heading == "Qute" && (
                  <Button
                    sx={{ textTransform: "capitalize", marginRight: "12px" }}
                    variant="contained"
                    onClick={handleFileUpload}
                    startIcon={<AddOutlinedIcon />}
                  >
                    Upload here
                  </Button>
                )}
                <Avatar src={""} alt="user image" />
                <Typography variant="h3" component={"h3"}>
                  {window.NIBRIam && window.NIBRIam.NIBRFull
                    ? window.NIBRIam.NIBRFull
                    : "User"}
                </Typography>
              </Grid>
            </Grid>
          </Grid>
          <Typography
            onMouseEnter={() => {
              (heading == "Qute" || heading == "Virtual Presenter") &&
                openQuteHeader();
            }}
            className={classes.warningmsg}
          >
            The content generated by Generative AI is intended to help and
            inspire, but users should verify information independently for
            accuracy and relevance.
          </Typography>
        </Grid>
      ) : (
        <Typography
          onMouseEnter={() => {
            (heading == "Qute" || heading == "Virtual Presenter") &&
              openQuteHeader();
          }}
          className={`${classes.warningmsg} ${classes.warningmsg2}`}
        >
          The content generated by Generative AI is intended to help and
          inspire, but users should verify information independently for
          accuracy and relevance.
        </Typography>
      )}
    </>
  );
}

export default withStyles((theme) => ({
  ...headerStyles(theme),
}))(Header);
