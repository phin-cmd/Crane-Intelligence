/**
 * Test data fixtures for consistent test data across tests
 */

export const testUsers = {
  regular: {
    email: 'test@craneintelligence.tech',
    password: 'TestPassword123!',
    firstName: 'Test',
    lastName: 'User',
    role: 'Crane Rental Company',
  },
  admin: {
    email: 'admin@craneintelligence.tech',
    password: 'AdminPassword123!',
    firstName: 'Admin',
    lastName: 'User',
    role: 'Admin',
  },
};

export const testCraneData = {
  spotCheck: {
    manufacturer: 'Liebherr',
    model: 'LTM 1100-4.2',
    year: 2020,
    capacity: 100,
    hours: 5000,
    condition: 'Excellent',
    location: 'United States',
  },
  professional: {
    manufacturer: 'Grove',
    model: 'GMK5250L',
    year: 2019,
    capacity: 250,
    hours: 8000,
    condition: 'Good',
    location: 'United States',
    serialNumber: 'TEST-SERIAL-001',
  },
  fleet: [
    {
      manufacturer: 'Liebherr',
      model: 'LTM 1100-4.2',
      year: 2020,
      capacity: 100,
      hours: 5000,
    },
    {
      manufacturer: 'Grove',
      model: 'GMK5250L',
      year: 2019,
      capacity: 250,
      hours: 8000,
    },
    {
      manufacturer: 'Manitowoc',
      model: 'MLC650',
      year: 2021,
      capacity: 650,
      hours: 3000,
    },
  ],
};

export const testReportData = {
  spotCheck: {
    type: 'Spot Check',
    price: 250,
    status: 'Payment Pending',
  },
  professional: {
    type: 'Professional',
    price: 995,
    status: 'Payment Pending',
  },
  fleet: {
    type: 'Fleet Valuation',
    price: 1495,
    status: 'Payment Pending',
  },
};

export const testPaymentData = {
  success: {
    cardNumber: '4242 4242 4242 4242',
    expiryDate: '12/25',
    cvc: '123',
    zipCode: '12345',
  },
  declined: {
    cardNumber: '4000 0000 0000 0002',
    expiryDate: '12/25',
    cvc: '123',
    zipCode: '12345',
  },
};

export const testNotificationData = {
  reportStatusUpdate: {
    type: 'report_status',
    title: 'Report Status Updated',
    message: 'Your FMV report status has been updated',
  },
  paymentConfirmation: {
    type: 'payment',
    title: 'Payment Confirmed',
    message: 'Your payment has been processed successfully',
  },
};

