import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Box,
  Typography,
  TablePagination,
  Tooltip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';

interface CustomerTableProps {
  customers: any[];
  onEdit: (customer: any) => void;
  onDelete: (id: number) => void;
  onView: (customer: any) => void;
  loading?: boolean;
}

const CustomerTable: React.FC<CustomerTableProps> = ({
  customers,
  onEdit,
  onDelete,
  onView,
  loading = false,
}) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'inactive':
        return 'default';
      case 'suspended':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active':
        return 'فعال';
      case 'inactive':
        return 'غیرفعال';
      case 'suspended':
        return 'معلق';
      default:
        return status;
    }
  };

  const getCustomerTypeLabel = (type: string) => {
    switch (type) {
      case 'individual':
        return 'حقیقی';
      case 'legal':
        return 'حقوقی';
      default:
        return type;
    }
  };

  return (
    <Paper>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>کد مشتری</TableCell>
              <TableCell>نام</TableCell>
              <TableCell>نوع</TableCell>
              <TableCell>تلفن</TableCell>
              <TableCell>ایمیل</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell>تاریخ ایجاد</TableCell>
              <TableCell>عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {customers
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((customer) => (
                <TableRow key={customer.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {customer.customer_code}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {customer.first_name} {customer.last_name}
                      </Typography>
                      {customer.company_name && (
                        <Typography variant="caption" color="text.secondary">
                          {customer.company_name}
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getCustomerTypeLabel(customer.customer_type)}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{customer.phone_number || '-'}</TableCell>
                  <TableCell>{customer.email || '-'}</TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(customer.status)}
                      color={getStatusColor(customer.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(customer.created_at).toLocaleDateString('fa-IR')}
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="مشاهده">
                        <IconButton
                          size="small"
                          onClick={() => onView(customer)}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="ویرایش">
                        <IconButton
                          size="small"
                          onClick={() => onEdit(customer)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="حذف">
                        <IconButton
                          size="small"
                          onClick={() => onDelete(customer.id)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={customers.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="تعداد ردیف در صفحه:"
        labelDisplayedRows={({ from, to, count }) =>
          `${from}-${to} از ${count}`
        }
      />
    </Paper>
  );
};

export default CustomerTable;