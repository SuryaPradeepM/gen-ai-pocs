const logoGeneratorStyles = (theme) => ({
  mainSection: {
    position: "absolute",
    left: 0,
    top: 94,
    bottom: 0,
    right: 0,
  },
  mainContent: {
    padding: theme.spacing(4),
  },
  mainTitle: {
    fontSize: "24px",
    fontWeight: 600,
    marginBottom: theme.spacing(3),
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
  },
  homeIcon: {
    cursor: "pointer",
    fontSize: "24px",
  },
  formContainer: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: theme.spacing(4),
  },
  inputSection: {
    backgroundColor: "#fff",
    padding: theme.spacing(3),
    borderRadius: theme.spacing(1),
    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
  },
  outputSection: {
    backgroundColor: "#fff",
    padding: theme.spacing(3),
    borderRadius: theme.spacing(1),
    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
  },
  sectionTitle: {
    fontSize: "18px",
    fontWeight: 500,
    marginBottom: theme.spacing(2),
  },
  formField: {
    marginBottom: theme.spacing(2),
  },
  chipContainer: {
    display: "flex",
    flexWrap: "wrap",
    gap: theme.spacing(1),
    marginTop: theme.spacing(1),
  },
  generateButton: {
    marginTop: theme.spacing(2),
    backgroundColor: "#0460A9",
    color: "#fff",
    "&:hover": {
      backgroundColor: "#034a8a",
    },
    "&.Mui-disabled": {
      backgroundColor: "#ccc",
    },
  },
  previewContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: theme.spacing(2),
    marginTop: theme.spacing(2),
  },
  logoPreview: {
    maxWidth: "100%",
    height: "auto",
    borderRadius: theme.spacing(1),
  },
  downloadButton: {
    marginTop: theme.spacing(2),
  },
  errorMessage: {
    color: theme.palette.error.main,
    marginTop: theme.spacing(2),
  },
});

export default logoGeneratorStyles;
