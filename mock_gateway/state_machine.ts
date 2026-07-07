/**
 * Onboarding State Machine & Interface Contracts
 * 
 * Target Flow:
 *   Step 1: Business Details Input (IDLE -> COLLECTING_BUSINESS_DETAILS)
 *   Step 2: Upload Documents (UPLOADING_KYC -> VERIFYING_KYC)
 *   Step 3: Connect alternate data (CONNECTING_DIGITAL_DATA -> POLLING_APIS)
 *   Action: Click Analyze (POLLING_APIS -> ANALYZING -> SUCCESS)
 *   Fallback: If APIs fail, transition UI state to Fallback Uploads (FALLBACK_UPLOADS)
 */

export interface BusinessDetails {
  businessName: string;
  panNumber: string;
  ownerName: string;
  industry: string;
  annualTurnover: number;
}

export interface KYCData {
  panCardFile: File | null;
  aadhaarNumber: string;
  udyamRegistrationNumber: string;
}

export interface FallbackUploads {
  bankStatementPdf: File | null;
  gstCertificatePdf: File | null;
}

export interface Metric {
  label: string;
  value: string | number;
  status?: 'success' | 'warning' | 'error';
}

export interface LoanRecommendation {
  approvedAmountInr: number;
  interestRatePct: number;
  tenureMonths: number;
  monthlyEmiInr: number;
  productType: string;
}

export interface EvaluationResult {
  healthScore: number;
  grade: string;
  recommendation: LoanRecommendation;
  riskExplanation: string[];
  creditMemoMarkdown: string;
}

// 1. Precise Onboarding States
export type OnboardingState =
  | 'IDLE'
  | 'COLLECTING_BUSINESS_DETAILS'  // Step 1: Input details
  | 'UPLOADING_KYC'                // Step 2: KYC document uploads
  | 'VERIFYING_KYC'                // Backend verification process for PAN/Aadhaar/Udyam
  | 'CONNECTING_DIGITAL_DATA'      // Step 3: Connect Buttons (GST, AA, UPI, EPFO)
  | 'POLLING_APIS'                 // Simulated polling for digital connections
  | 'FALLBACK_UPLOADS'             // Fallback screen for statement/GST certificate upload if APIs fail
  | 'ANALYZING'                    // Trigger Credit Copilot evaluation
  | 'SUCCESS'                      // Success screen with credit offer and memo
  | 'FAILED';                      // Error screen for unrecoverable issues (e.g. KYC verification fails)

// 2. State Machine Events
export type OnboardingEvent =
  | { type: 'START' }
  | { type: 'SUBMIT_BUSINESS_DETAILS'; payload: BusinessDetails }
  | { type: 'SUBMIT_KYC_DOCUMENTS'; payload: KYCData }
  | { type: 'KYC_VERIFICATION_SUCCESS' }
  | { type: 'KYC_VERIFICATION_FAILURE'; reason: string }
  | { type: 'CONNECT_API_SOURCE'; source: 'GST' | 'AA' | 'UPI' | 'EPFO' }
  | { type: 'API_CONNECTION_SUCCESS' }
  | { type: 'API_CONNECTION_FAILURE'; reason: string }
  | { type: 'SUBMIT_FALLBACK_UPLOADS'; payload: FallbackUploads }
  | { type: 'CLICK_ANALYZE' }
  | { type: 'ANALYSIS_SUCCESS'; payload: EvaluationResult }
  | { type: 'ANALYSIS_FAILURE'; reason: string }
  | { type: 'RESET' };

// 3. Form Context Data Store
export interface OnboardingContext {
  currentState: OnboardingState;
  businessDetails: BusinessDetails | null;
  kycData: KYCData | null;
  connectedAPIs: {
    GST: boolean;
    AA: boolean;
    UPI: boolean;
    EPFO: boolean;
  };
  fallbackUploads: FallbackUploads | null;
  evaluationResult: EvaluationResult | null;
  errorMessage: string | null;
}

export const initialContext: OnboardingContext = {
  currentState: 'IDLE',
  businessDetails: null,
  kycData: null,
  connectedAPIs: {
    GST: false,
    AA: false,
    UPI: false,
    EPFO: false,
  },
  fallbackUploads: null,
  evaluationResult: null,
  errorMessage: null,
};

/**
 * State Transition Reducer / State Machine Engine
 * Pure function describing state transitions and context updates
 */
export function transition(
  context: OnboardingContext,
  event: OnboardingEvent
): OnboardingContext {
  const state = context.currentState;

  switch (state) {
    case 'IDLE':
      if (event.type === 'START') {
        return { ...context, currentState: 'COLLECTING_BUSINESS_DETAILS' };
      }
      break;

    case 'COLLECTING_BUSINESS_DETAILS':
      if (event.type === 'SUBMIT_BUSINESS_DETAILS') {
        return {
          ...context,
          businessDetails: event.payload,
          currentState: 'UPLOADING_KYC',
        };
      }
      break;

    case 'UPLOADING_KYC':
      if (event.type === 'SUBMIT_KYC_DOCUMENTS') {
        return {
          ...context,
          kycData: event.payload,
          currentState: 'VERIFYING_KYC',
        };
      }
      break;

    case 'VERIFYING_KYC':
      if (event.type === 'KYC_VERIFICATION_SUCCESS') {
        return {
          ...context,
          currentState: 'CONNECTING_DIGITAL_DATA',
        };
      }
      if (event.type === 'KYC_VERIFICATION_FAILURE') {
        return {
          ...context,
          currentState: 'FAILED',
          errorMessage: event.reason,
        };
      }
      break;

    case 'CONNECTING_DIGITAL_DATA':
      if (event.type === 'CONNECT_API_SOURCE') {
        const nextConnected = { ...context.connectedAPIs, [event.source]: true };
        const allConnected = Object.values(nextConnected).every(val => val === true);
        return {
          ...context,
          connectedAPIs: nextConnected,
          currentState: allConnected ? 'POLLING_APIS' : 'CONNECTING_DIGITAL_DATA',
        };
      }
      if (event.type === 'API_CONNECTION_FAILURE') {
        // Core API Connection Failed -> Transition directly to Fallback Upload Form
        return {
          ...context,
          currentState: 'FALLBACK_UPLOADS',
          errorMessage: event.reason,
        };
      }
      break;

    case 'POLLING_APIS':
      if (event.type === 'API_CONNECTION_SUCCESS') {
        return {
          ...context,
          currentState: 'POLLING_APIS', // Stay in polling until Click Analyze trigger
        };
      }
      if (event.type === 'CLICK_ANALYZE') {
        return {
          ...context,
          currentState: 'ANALYZING',
        };
      }
      if (event.type === 'API_CONNECTION_FAILURE') {
        // Connection lost or API error during polling -> Transition to Fallback Flow
        return {
          ...context,
          currentState: 'FALLBACK_UPLOADS',
          errorMessage: event.reason,
        };
      }
      break;

    case 'FALLBACK_UPLOADS':
      if (event.type === 'SUBMIT_FALLBACK_UPLOADS') {
        return {
          ...context,
          fallbackUploads: event.payload,
          currentState: 'ANALYZING',
        };
      }
      break;

    case 'ANALYZING':
      if (event.type === 'ANALYSIS_SUCCESS') {
        return {
          ...context,
          evaluationResult: event.payload,
          currentState: 'SUCCESS',
        };
      }
      if (event.type === 'ANALYSIS_FAILURE') {
        return {
          ...context,
          currentState: 'FAILED',
          errorMessage: event.reason,
        };
      }
      break;

    case 'SUCCESS':
    case 'FAILED':
      if (event.type === 'RESET') {
        return { ...initialContext, currentState: 'IDLE' };
      }
      break;
  }

  return context; // Ignore invalid transitions
}
