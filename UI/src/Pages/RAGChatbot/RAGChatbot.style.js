import { styled } from "@mui/material/styles";
import { Container } from "@mui/material";

export const StyledContainer = styled(Container)(({ theme }) => ({
  paddingTop: theme.spacing(4),
  paddingBottom: theme.spacing(4),
}));

export const MessageContainer = styled("div")({
  flex: 1,
  overflow: "auto",
  padding: "20px",
  display: "flex",
  flexDirection: "column",
  gap: "10px",
});

export const Message = styled("div")(({ theme, role }) => ({
  maxWidth: "70%",
  padding: "10px 15px",
  borderRadius: "10px",
  alignSelf: role === "user" ? "flex-end" : "flex-start",
  backgroundColor:
    role === "user" ? theme.palette.primary.main : theme.palette.grey[100],
  color:
    role === "user"
      ? theme.palette.primary.contrastText
      : theme.palette.text.primary,
}));

export const FileUploadSection = styled("div")(({ theme }) => ({
  marginBottom: theme.spacing(3),
  display: "flex",
  alignItems: "center",
  gap: theme.spacing(2),
}));
