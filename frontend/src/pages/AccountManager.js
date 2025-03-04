import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Grid,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Upload as UploadIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { DataGrid } from '@mui/x-data-grid';
import { useSnackbar } from 'notistack';
import axios from 'axios';
import * as Yup from 'yup';
import { useFormik } from 'formik';

const validationSchema = Yup.object({
  username: Yup.string()
    .required('Username is required')
    .min(3, 'Username must be at least 3 characters'),
  password: Yup.string()
    .required('Password is required')
    .min(6, 'Password must be at least 6 characters'),
});

const AccountManager = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openUploadDialog, setOpenUploadDialog] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const { enqueueSnackbar } = useSnackbar();

  const formik = useFormik({
    initialValues: {
      username: '',
      password: '',
    },
    validationSchema,
    onSubmit: async (values, { setSubmitting, resetForm }) => {
      try {
        // In a real application, make API call to add account
        const response = await axios.post('/api/v1/accounts', values);
        
        enqueueSnackbar('Account added successfully', { variant: 'success' });
        setOpenAddDialog(false);
        resetForm();
        fetchAccounts();
      } catch (error) {
        enqueueSnackbar(error.response?.data?.message || 'Failed to add account', {
          variant: 'error',
        });
      } finally {
        setSubmitting(false);
      }
    },
  });

  const fetchAccounts = async () => {
    setLoading(true);
    try {
      // In a real application, make API call to fetch accounts
      const response = await axios.get('/api/v1/accounts');
      setAccounts(response.data.accounts);
    } catch (error) {
      enqueueSnackbar('Failed to fetch accounts', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type !== 'text/csv') {
        enqueueSnackbar('Please upload a CSV file', { variant: 'error' });
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleBulkUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('/api/v1/accounts/bulk', formData, {
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(progress);
        },
      });

      enqueueSnackbar('Accounts uploaded successfully', { variant: 'success' });
      setOpenUploadDialog(false);
      setSelectedFile(null);
      setUploadProgress(0);
      fetchAccounts();
    } catch (error) {
      enqueueSnackbar(error.response?.data?.message || 'Failed to upload accounts', {
        variant: 'error',
      });
    }
  };

  const handleDeleteAccount = async (username) => {
    try {
      await axios.delete(`/api/v1/accounts/${username}`);
      enqueueSnackbar('Account deleted successfully', { variant: 'success' });
      fetchAccounts();
    } catch (error) {
      enqueueSnackbar('Failed to delete account', { variant: 'error' });
    }
  };

  const columns = [
    { field: 'username', headerName: 'Username', flex: 1 },
    {
      field: 'status',
      headerName: 'Status',
      flex: 1,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={params.value === 'active' ? 'success' : 'error'}
          size="small"
          icon={params.value === 'active' ? <CheckCircleIcon /> : <ErrorIcon />}
        />
      ),
    },
    {
      field: 'lastLogin',
      headerName: 'Last Login',
      flex: 1,
      valueFormatter: (params) =>
        params.value ? new Date(params.value).toLocaleString() : 'Never',
    },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 1,
      sortable: false,
      renderCell: (params) => (
        <Box>
          <IconButton
            color="error"
            onClick={() => handleDeleteAccount(params.row.username)}
          >
            <DeleteIcon />
          </IconButton>
        </Box>
      ),
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Account Manager
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenAddDialog(true)}
            sx={{ mr: 2 }}
          >
            Add Account
          </Button>
          <Button
            variant="outlined"
            startIcon={<UploadIcon />}
            onClick={() => setOpenUploadDialog(true)}
          >
            Bulk Upload
          </Button>
        </Box>
      </Box>

      <Card>
        <CardContent>
          <Box sx={{ height: 400, width: '100%' }}>
            <DataGrid
              rows={accounts}
              columns={columns}
              pageSize={5}
              rowsPerPageOptions={[5, 10, 20]}
              checkboxSelection
              disableSelectionOnClick
              loading={loading}
              getRowId={(row) => row.username}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Add Account Dialog */}
      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)}>
        <DialogTitle>Add Instagram Account</DialogTitle>
        <form onSubmit={formik.handleSubmit}>
          <DialogContent>
            <TextField
              fullWidth
              id="username"
              name="username"
              label="Username"
              margin="normal"
              value={formik.values.username}
              onChange={formik.handleChange}
              error={formik.touched.username && Boolean(formik.errors.username)}
              helperText={formik.touched.username && formik.errors.username}
            />
            <TextField
              fullWidth
              id="password"
              name="password"
              label="Password"
              type="password"
              margin="normal"
              value={formik.values.password}
              onChange={formik.handleChange}
              error={formik.touched.password && Boolean(formik.errors.password)}
              helperText={formik.touched.password && formik.errors.password}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenAddDialog(false)}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={formik.isSubmitting}
            >
              {formik.isSubmitting ? 'Adding...' : 'Add Account'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Bulk Upload Dialog */}
      <Dialog open={openUploadDialog} onClose={() => setOpenUploadDialog(false)}>
        <DialogTitle>Bulk Upload Accounts</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Upload a CSV file with columns: username, password
          </Alert>
          <input
            accept=".csv"
            style={{ display: 'none' }}
            id="raised-button-file"
            type="file"
            onChange={handleFileUpload}
          />
          <label htmlFor="raised-button-file">
            <Button variant="outlined" component="span">
              Choose CSV File
            </Button>
          </label>
          {selectedFile && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected file: {selectedFile.name}
            </Typography>
          )}
          {uploadProgress > 0 && (
            <Box sx={{ mt: 2 }}>
              <CircularProgress variant="determinate" value={uploadProgress} />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenUploadDialog(false)}>Cancel</Button>
          <Button
            onClick={handleBulkUpload}
            variant="contained"
            disabled={!selectedFile}
          >
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AccountManager;
