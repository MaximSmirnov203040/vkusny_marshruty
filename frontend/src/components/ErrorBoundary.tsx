import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button } from '@mui/material';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="100vh"
          p={3}
          textAlign="center"
        >
          <Typography variant="h4" component="h1" gutterBottom color="error">
            Упс! Что-то пошло не так
          </Typography>
          <Typography variant="body1" color="text.secondary" mb={4}>
            Произошла ошибка при загрузке страницы. Пожалуйста, попробуйте обновить страницу.
          </Typography>
          {process.env.NODE_ENV === 'development' && (
            <Typography
              variant="body2"
              color="text.secondary"
              component="pre"
              sx={{
                maxWidth: '100%',
                overflow: 'auto',
                bgcolor: 'grey.100',
                p: 2,
                borderRadius: 1,
                mb: 4,
              }}
            >
              {this.state.error?.toString()}
            </Typography>
          )}
          <Button
            variant="contained"
            color="primary"
            onClick={this.handleReload}
            size="large"
          >
            Обновить страницу
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 