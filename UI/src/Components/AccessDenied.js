import { Container, Typography, Box } from "@mui/material";

const AccessDenied = () => {
  return (
    <Container maxWidth="sm">
      <Box mt={4} textAlign="center">
        <Typography variant="h4" gutterBottom>
          Access Denied
        </Typography>
        <Typography variant="body1">
          You don't have permission to view the contents of this site.
        </Typography>
        <Box mt={2}>
          <Typography variant="body1">
            Please contact the administrator to request access.
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default AccessDenied;
