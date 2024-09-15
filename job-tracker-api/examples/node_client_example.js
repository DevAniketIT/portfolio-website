#!/usr/bin/env node
/**
 * Node.js Client Example for Job Application Tracker API
 * 
 * Features:
 * - Uses axios for HTTP requests with better Node.js support
 * - Environment variable configuration
 * - File-based data import example
 * - Comprehensive error handling
 * - Bulk operations support
 * - Progress reporting
 * - Retry logic with exponential backoff
 * 
 * Usage:
 *   node node_client_example.js
 *   API_BASE_URL=https://your-api.onrender.com node node_client_example.js
 *   API_BASE_URL=https://your-api.com API_KEY=your-key node node_client_example.js
 */

import axios from 'axios';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration from environment variables
const config = {
  baseURL: process.env.API_BASE_URL || 'https://your-service-name.onrender.com',
  apiKey: process.env.API_KEY || null,
  timeout: parseInt(process.env.REQUEST_TIMEOUT) || 30000,
  retryAttempts: parseInt(process.env.RETRY_ATTEMPTS) || 3,
  retryDelay: parseInt(process.env.RETRY_DELAY_MS) || 1000,
};

console.log(`🔧 Configuration:
  Base URL: ${config.baseURL}
  API Key: ${config.apiKey ? '***' + config.apiKey.slice(-4) : 'Not set'}
  Timeout: ${config.timeout}ms
  Retry Attempts: ${config.retryAttempts}
`);

// Create axios instance with default configuration
const api = axios.create({
  baseURL: config.baseURL,
  timeout: config.timeout,
  headers: {
    'Content-Type': 'application/json',
    ...(config.apiKey && { 'X-API-Key': config.apiKey }),
  },
});

// Add retry interceptor with exponential backoff
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config: requestConfig } = error;
    
    if (!requestConfig || requestConfig.__retryCount >= config.retryAttempts) {
      return Promise.reject(error);
    }
    
    requestConfig.__retryCount = requestConfig.__retryCount || 0;
    requestConfig.__retryCount++;
    
    // Only retry on network errors and 5xx server errors
    const shouldRetry = !error.response || (error.response.status >= 500);
    if (!shouldRetry) {
      return Promise.reject(error);
    }
    
    const delay = config.retryDelay * Math.pow(2, requestConfig.__retryCount - 1);
    console.log(`⏳ Retrying request ${requestConfig.__retryCount}/${config.retryAttempts} after ${delay}ms...`);
    
    await new Promise(resolve => setTimeout(resolve, delay));
    return api(requestConfig);
  }
);

// Enhanced error handling
function handleError(error, operation = 'API operation') {
  console.error(`❌ ${operation} failed:`);
  
  if (error.response) {
    // Server responded with error status
    console.error(`  Status: ${error.response.status}`);
    console.error(`  Message: ${error.response.data?.message || error.response.statusText}`);
    if (error.response.data?.errors) {
      console.error(`  Errors: ${error.response.data.errors.join(', ')}`);
    }
  } else if (error.request) {
    // Request was made but no response received
    console.error(`  Network Error: ${error.message}`);
    console.error(`  Check if API server is running at: ${config.baseURL}`);
  } else {
    // Something else happened
    console.error(`  Error: ${error.message}`);
  }
}

// CRUD Operations
export async function createApplication(data) {
  try {
    const response = await api.post('/api/applications/', data);
    return response.data;
  } catch (error) {
    handleError(error, 'Create application');
    throw error;
  }
}

export async function getApplication(id) {
  try {
    const response = await api.get(`/api/applications/${id}`);
    return response.data;
  } catch (error) {
    handleError(error, `Get application ${id}`);
    throw error;
  }
}

export async function listApplications(params = {}) {
  try {
    const response = await api.get('/api/applications/', { params });
    return response.data;
  } catch (error) {
    handleError(error, 'List applications');
    throw error;
  }
}

export async function updateApplication(id, data) {
  try {
    const response = await api.put(`/api/applications/${id}`, data);
    return response.data;
  } catch (error) {
    handleError(error, `Update application ${id}`);
    throw error;
  }
}

export async function updateApplicationStatus(id, status) {
  try {
    const response = await api.patch(`/api/applications/${id}/status`, null, {
      params: { status }
    });
    return response.data;
  } catch (error) {
    handleError(error, `Update status for application ${id}`);
    throw error;
  }
}

export async function deleteApplication(id) {
  try {
    const response = await api.delete(`/api/applications/${id}`);
    return response.data;
  } catch (error) {
    handleError(error, `Delete application ${id}`);
    throw error;
  }
}

// Tracking API
export async function quickTrack(data) {
  try {
    const response = await api.post('/api/tracking/track', data);
    return response.data;
  } catch (error) {
    handleError(error, 'Quick track');
    throw error;
  }
}

export async function getAnalyticsStats() {
  try {
    const response = await api.get('/api/tracking/stats');
    return response.data;
  } catch (error) {
    handleError(error, 'Get analytics stats');
    throw error;
  }
}

export async function getApplicationHistory(id) {
  try {
    const response = await api.get(`/api/tracking/application-history/${id}`);
    return response.data;
  } catch (error) {
    handleError(error, `Get application history for ${id}`);
    throw error;
  }
}

export async function addInteraction(appId, interactionData) {
  try {
    const response = await api.post(
      `/api/tracking/application-history/${appId}/interaction`,
      null,
      { params: interactionData }
    );
    return response.data;
  } catch (error) {
    handleError(error, `Add interaction to application ${appId}`);
    throw error;
  }
}

export async function getRecentActivity(params = {}) {
  try {
    const response = await api.get('/api/tracking/recent-activity', { params });
    return response.data;
  } catch (error) {
    handleError(error, 'Get recent activity');
    throw error;
  }
}

// Health check
export async function healthCheck() {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    handleError(error, 'Health check');
    throw error;
  }
}

// File-based data import example
export async function loadApplicationsFromFile(filePath) {
  try {
    console.log(`📂 Loading applications from: ${filePath}`);
    const data = await fs.readFile(filePath, 'utf8');
    const applications = JSON.parse(data);
    
    if (!Array.isArray(applications)) {
      throw new Error('File must contain an array of applications');
    }
    
    console.log(`📊 Found ${applications.length} applications to import`);
    return applications;
  } catch (error) {
    console.error(`❌ Failed to load file: ${error.message}`);
    throw error;
  }
}

// Bulk operations with progress reporting
export async function bulkCreateApplications(applications, batchSize = 5) {
  const results = [];
  const totalBatches = Math.ceil(applications.length / batchSize);
  
  console.log(`🚀 Starting bulk creation: ${applications.length} apps in ${totalBatches} batches`);
  
  for (let i = 0; i < applications.length; i += batchSize) {
    const batch = applications.slice(i, i + batchSize);
    const batchNumber = Math.floor(i / batchSize) + 1;
    
    console.log(`📦 Processing batch ${batchNumber}/${totalBatches} (${batch.length} items)...`);
    
    const batchPromises = batch.map(async (app, index) => {
      try {
        const result = await createApplication(app);
        console.log(`  ✅ Created: ${app.company_name} - ${app.job_title}`);
        return { success: true, data: result, originalData: app };
      } catch (error) {
        console.log(`  ❌ Failed: ${app.company_name} - ${app.job_title} (${error.response?.data?.message || error.message})`);
        return { success: false, error: error.message, originalData: app };
      }
    });
    
    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);
    
    // Add delay between batches to avoid rate limiting
    if (i + batchSize < applications.length) {
      console.log('⏳ Waiting 1 second before next batch...');
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  const successful = results.filter(r => r.success).length;
  const failed = results.length - successful;
  
  console.log(`📈 Bulk creation complete: ${successful} successful, ${failed} failed`);
  return results;
}

// Sample data for testing
const sampleApplications = [
  {
    company_name: 'TechCorp Inc',
    job_title: 'Senior Software Engineer',
    location: 'San Francisco, CA',
    job_type: 'full_time',
    remote_type: 'hybrid',
    salary_min: 120000,
    salary_max: 180000,
    status: 'applied',
    priority: 'high',
    notes: 'Applied through company website'
  },
  {
    company_name: 'DataWorks Ltd',
    job_title: 'Data Engineer',
    location: 'New York, NY',
    job_type: 'full_time',
    remote_type: 'remote',
    salary_min: 100000,
    salary_max: 150000,
    status: 'applied',
    priority: 'medium',
    notes: 'Referred by former colleague'
  },
  {
    company_name: 'AI Startup',
    job_title: 'Machine Learning Engineer',
    location: 'Seattle, WA',
    job_type: 'full_time',
    remote_type: 'remote',
    salary_min: 130000,
    salary_max: 200000,
    status: 'applied',
    priority: 'urgent',
    notes: 'Exciting AI company, great team'
  }
];

// Demo functions
async function demonstrateBasicOperations() {
  console.log('\n🔨 === BASIC CRUD OPERATIONS ===');
  
  try {
    // Create
    console.log('\n1️⃣ Creating application...');
    const created = await createApplication({
      company_name: 'Demo Corp',
      job_title: 'Node.js Developer',
      status: 'applied',
      notes: 'Created via Node.js client'
    });
    console.log(`✅ Created application with ID: ${created.data?.id || created.id}`);
    const appId = created.data?.id || created.id;
    
    // Read
    console.log('\n2️⃣ Fetching application...');
    const fetched = await getApplication(appId);
    console.log(`✅ Fetched: ${fetched.data?.company_name || fetched.company_name} - ${fetched.data?.job_title || fetched.job_title}`);
    
    // Update
    console.log('\n3️⃣ Updating application...');
    await updateApplication(appId, {
      status: 'reviewing',
      notes: 'Updated via Node.js client - moved to review stage'
    });
    console.log('✅ Updated application');
    
    // Status update
    console.log('\n4️⃣ Updating status...');
    await updateApplicationStatus(appId, 'phone_screen');
    console.log('✅ Status updated to phone_screen');
    
    // List
    console.log('\n5️⃣ Listing applications...');
    const list = await listApplications({ limit: 5 });
    const total = list.total || list.items?.length || 0;
    console.log(`✅ Found ${total} applications`);
    
    return appId;
  } catch (error) {
    console.error('❌ Basic operations failed:', error.message);
    return null;
  }
}

async function demonstrateTrackingFeatures() {
  console.log('\n📊 === TRACKING & ANALYTICS ===');
  
  try {
    // Quick track
    console.log('\n1️⃣ Quick tracking...');
    const tracked = await quickTrack({
      company: 'QuickTrack Inc',
      title: 'Backend Developer',
      url: 'https://quicktrack.com/jobs/123',
      notes: 'Found via job board'
    });
    console.log(`✅ Quick tracked: ${tracked.company} - ${tracked.title}`);
    
    // Analytics
    console.log('\n2️⃣ Getting analytics...');
    const stats = await getAnalyticsStats();
    console.log(`✅ Analytics:
      Total Applications: ${stats.total_applications || 0}
      Success Rate: ${stats.success_rate || 0}%
      Active Applications: ${stats.active_applications || 0}
      Average Response Time: ${stats.average_response_time || 0} days`);
    
    // Recent activity
    console.log('\n3️⃣ Recent activity...');
    const activity = await getRecentActivity({ days: 7, limit: 5 });
    const recentItems = activity.recent_activity || [];
    console.log(`✅ Found ${recentItems.length} recent activities`);
    
    return tracked.tracking_id || tracked.id;
  } catch (error) {
    console.error('❌ Tracking demo failed:', error.message);
    return null;
  }
}

async function demonstrateFileImport() {
  console.log('\n📁 === FILE IMPORT DEMO ===');
  
  try {
    // Create sample data file
    const sampleFile = path.join(__dirname, 'sample_applications.json');
    await fs.writeFile(sampleFile, JSON.stringify(sampleApplications, null, 2));
    console.log(`✅ Created sample file: ${sampleFile}`);
    
    // Load and import
    const applications = await loadApplicationsFromFile(sampleFile);
    const results = await bulkCreateApplications(applications, 2);
    
    // Cleanup sample file
    await fs.unlink(sampleFile);
    console.log('✅ Cleaned up sample file');
    
    return results;
  } catch (error) {
    console.error('❌ File import demo failed:', error.message);
    return [];
  }
}

async function demonstrateHealthCheck() {
  console.log('\n🏥 === HEALTH CHECK ===');
  
  try {
    const health = await healthCheck();
    console.log(`✅ API Health: ${health.status || 'OK'}`);
    if (health.database_status) {
      console.log(`✅ Database: ${health.database_status}`);
    }
    return true;
  } catch (error) {
    console.error('❌ Health check failed');
    console.error('💡 Ensure the API server is running and accessible');
    return false;
  }
}

// Cleanup function to remove demo data
async function cleanup(createdIds) {
  console.log('\n🧹 === CLEANUP ===');
  
  let cleaned = 0;
  for (const id of createdIds) {
    try {
      await deleteApplication(id);
      cleaned++;
      console.log(`✅ Deleted application ${id}`);
    } catch (error) {
      console.log(`⚠️  Failed to delete application ${id}: ${error.message}`);
    }
  }
  
  console.log(`🧹 Cleanup complete: ${cleaned}/${createdIds.length} applications deleted`);
}

// Main demo function
async function main() {
  console.log('🚀 Job Tracker API - Node.js Client Demo\n');
  console.log('='.repeat(50));
  
  const createdIds = [];
  
  try {
    // Health check first
    const isHealthy = await demonstrateHealthCheck();
    if (!isHealthy) {
      console.log('\n❌ API is not healthy. Please check your API server and configuration.');
      console.log('💡 Set API_BASE_URL environment variable to your API endpoint.');
      return;
    }
    
    // Basic CRUD operations
    const basicDemoId = await demonstrateBasicOperations();
    if (basicDemoId) createdIds.push(basicDemoId);
    
    // Tracking features
    const trackingId = await demonstrateTrackingFeatures();
    if (trackingId) createdIds.push(trackingId);
    
    // File import demo
    const importResults = await demonstrateFileImport();
    const successfulImports = importResults.filter(r => r.success);
    successfulImports.forEach(result => {
      const id = result.data?.data?.id || result.data?.id;
      if (id) createdIds.push(id);
    });
    
    console.log('\n🎉 === DEMO COMPLETE ===');
    console.log(`✅ Successfully demonstrated all features`);
    console.log(`📊 Created ${createdIds.length} demo applications`);
    
  } catch (error) {
    console.error('\n💥 Demo failed with unexpected error:', error.message);
  } finally {
    // Clean up demo data
    if (createdIds.length > 0) {
      await cleanup(createdIds);
    }
  }
}

// Run demo if this file is executed directly
if (process.argv[1] === __filename || process.argv[1]?.includes('node_client_example')) {
  main().catch(console.error);
}
