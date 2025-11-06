import { createTheme } from "@mui/material/styles";
import "./Fonts/volta/fonts.css";

const applicationTheme = createTheme({
  components: {
    MuiTypography: {
      defaultProps: {
        fontFamily:
          '"regular", Arial, "Helvetica Neue", Helvetica, Roboto, sans-serif',
      },
    },
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          // backgroundColor: "#fff",
          color: "#000",
          overflow: "hidden",
          margin: 0,
          padding: 0,
          fontFamily:
            '"regular", Arial, "Helvetica Neue", Helvetica, Roboto, sans-serif',
          flex: 1,
          scrollBehavior: "smooth",
        },
      },
    },
  },
  breakpoints: {
    values: {
      ss: 600,
      xs: 959,
      sm: 1098,
      md: 1281,
      lg: 1537,
      xl: 1921,
    },
  },
  typography: {
    useNextVariants: true,
  },
  palette: {
    primary: {
      main: "#002068",
      light: "#e3e3e3",
      black: "#000",
      white: "#fff",
    },
    secondary: {
      main: "#0B61A9",
    },
  },
  overrides: {},
});

export default applicationTheme;
