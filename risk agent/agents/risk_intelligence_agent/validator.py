"""Data validation component for Risk Intelligence Agent.

This module implements exhaustive validation for MSME credit evaluation inputs.
It validates all required fields, formats, and data quality constraints before
processing begins.

Validation is performed exhaustively - all errors are collected before returning,
rather than failing on the first error.
"""

from typing import Union
from datetime import date
import re
from pydantic import ValidationError as PydanticValidationError

from .schemas import (
    MSMEInput,
    ValidatedData,
    ValidationError
)


def validate(data: dict) -> Union[ValidatedData, list[ValidationError]]:
    """Validate MSME input data for completeness and correctness.
    
    Performs exhaustive validation collecting all errors before returning.
    
    Args:
        data: Raw input dictionary containing MSME data
        
    Returns:
        ValidatedData with status="VALIDATED" on success, or
        list[ValidationError] containing all validation failures
        
    Validation Rules:
        1. Required fields: GSTIN, PAN, UPI transactions, bank statements
        2. GSTIN format: ^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$
        3. PAN format: ^[A-Z]{5}[0-9]{4}[A-Z]{1}$
        4. UPI transactions: must have amount, timestamp, counterparty
        5. UPI amounts: must be positive with max 2 decimal places
        6. Bank statement: must span >= 90 consecutive days from end date
    """
    errors: list[ValidationError] = []
    
    # Step 1: Check for required top-level fields
    required_fields = ['gstin', 'pan', 'upi_transactions', 'account_aggregator_data', 
                       'gst_data', 'business_registration_date']
    
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(ValidationError(
                field=field,
                error=f"Required field '{field}' is missing",
                value=None
            ))
        elif isinstance(data.get(field), str) and not data[field].strip():
            errors.append(ValidationError(
                field=field,
                error=f"Required field '{field}' contains only whitespace",
                value=data[field]
            ))
    
    # Step 2: Validate GSTIN format
    if 'gstin' in data and data['gstin']:
        gstin = str(data['gstin']).strip()
        gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(gstin_pattern, gstin):
            errors.append(ValidationError(
                field='gstin',
                error='GSTIN format invalid. Expected pattern: [0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}',
                value=gstin
            ))
    
    # Step 3: Validate PAN format
    if 'pan' in data and data['pan']:
        pan = str(data['pan']).strip()
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if not re.match(pan_pattern, pan):
            errors.append(ValidationError(
                field='pan',
                error='PAN format invalid. Expected pattern: [A-Z]{5}[0-9]{4}[A-Z]{1}',
                value=pan
            ))
    
    # Step 4: Validate UPI transactions structure
    if 'upi_transactions' in data and data['upi_transactions'] is not None:
        if not isinstance(data['upi_transactions'], list):
            errors.append(ValidationError(
                field='upi_transactions',
                error='UPI transactions must be a list',
                value=str(type(data['upi_transactions']))
            ))
        elif len(data['upi_transactions']) == 0:
            errors.append(ValidationError(
                field='upi_transactions',
                error='UPI transactions list is empty',
                value='[]'
            ))
        else:
            for idx, txn in enumerate(data['upi_transactions']):
                if not isinstance(txn, dict):
                    errors.append(ValidationError(
                        field=f'upi_transactions[{idx}]',
                        error='Transaction must be a dictionary',
                        value=str(type(txn))
                    ))
                    continue
                
                # Check required transaction fields
                required_txn_fields = ['amount', 'timestamp', 'counterparty']
                for txn_field in required_txn_fields:
                    if txn_field not in txn or txn[txn_field] is None:
                        errors.append(ValidationError(
                            field=f'upi_transactions[{idx}].{txn_field}',
                            error=f'Required field "{txn_field}" is missing in transaction',
                            value=None
                        ))
                    elif txn_field == 'counterparty' and isinstance(txn[txn_field], str) and not txn[txn_field].strip():
                        errors.append(ValidationError(
                            field=f'upi_transactions[{idx}].{txn_field}',
                            error='Counterparty field contains only whitespace',
                            value=txn[txn_field]
                        ))
                
                # Validate amount is positive and has max 2 decimal places
                if 'amount' in txn and txn['amount'] is not None:
                    try:
                        amount = float(txn['amount'])
                        if amount <= 0:
                            errors.append(ValidationError(
                                field=f'upi_transactions[{idx}].amount',
                                error='Transaction amount must be positive',
                                value=str(amount)
                            ))
                        # Check decimal places
                        if round(amount, 2) != amount:
                            errors.append(ValidationError(
                                field=f'upi_transactions[{idx}].amount',
                                error='Transaction amount must have maximum 2 decimal places',
                                value=str(amount)
                            ))
                    except (ValueError, TypeError):
                        errors.append(ValidationError(
                            field=f'upi_transactions[{idx}].amount',
                            error='Transaction amount must be a valid number',
                            value=str(txn['amount'])
                        ))
    
    # Step 5: Validate bank statement date range
    if 'account_aggregator_data' in data and data['account_aggregator_data'] is not None:
        aa_data = data['account_aggregator_data']
        if isinstance(aa_data, dict):
            if 'statement_start_date' not in aa_data or aa_data['statement_start_date'] is None:
                errors.append(ValidationError(
                    field='account_aggregator_data.statement_start_date',
                    error='Bank statement start date is required',
                    value=None
                ))
            if 'statement_end_date' not in aa_data or aa_data['statement_end_date'] is None:
                errors.append(ValidationError(
                    field='account_aggregator_data.statement_end_date',
                    error='Bank statement end date is required',
                    value=None
                ))
            
            # Validate date range if both dates are present
            if ('statement_start_date' in aa_data and aa_data['statement_start_date'] is not None and
                'statement_end_date' in aa_data and aa_data['statement_end_date'] is not None):
                try:
                    # Handle both date objects and string dates
                    if isinstance(aa_data['statement_start_date'], str):
                        start_date = date.fromisoformat(aa_data['statement_start_date'])
                    else:
                        start_date = aa_data['statement_start_date']
                    
                    if isinstance(aa_data['statement_end_date'], str):
                        end_date = date.fromisoformat(aa_data['statement_end_date'])
                    else:
                        end_date = aa_data['statement_end_date']
                    
                    days_span = (end_date - start_date).days
                    if days_span < 90:
                        errors.append(ValidationError(
                            field='account_aggregator_data.statement_end_date',
                            error=f'Bank statement must span at least 90 consecutive days, got {days_span} days',
                            value=f'{start_date} to {end_date}'
                        ))
                except (ValueError, TypeError, AttributeError) as e:
                    errors.append(ValidationError(
                        field='account_aggregator_data.date_range',
                        error=f'Invalid date format: {str(e)}',
                        value=f'{aa_data.get("statement_start_date")} to {aa_data.get("statement_end_date")}'
                    ))
    
    # Step 6: Validate GST data nested structure
    if 'gst_data' in data and data['gst_data'] is not None:
        gst_data = data['gst_data']
        if isinstance(gst_data, dict):
            # Validate GSTIN in gst_data matches top-level GSTIN
            if 'gstin' in gst_data and gst_data['gstin']:
                gst_gstin = str(gst_data['gstin']).strip()
                gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
                if not re.match(gstin_pattern, gst_gstin):
                    errors.append(ValidationError(
                        field='gst_data.gstin',
                        error='GSTIN format invalid in GST data',
                        value=gst_gstin
                    ))
    
    # If we collected any errors, return them
    if errors:
        return errors
    
    # Step 7: Try to construct and validate using Pydantic models
    try:
        msme_input = MSMEInput(**data)
        
        # Determine available data sources
        data_sources = ['GST', 'UPI', 'Account_Aggregator']
        if data.get('epfo_data'):
            data_sources.append('EPFO')
        if data.get('bank_data'):
            data_sources.append('Bank')
        
        # Return validated data
        return ValidatedData(
            status="VALIDATED",
            data=msme_input,
            data_sources_available=data_sources
        )
    
    except PydanticValidationError as e:
        # Convert Pydantic validation errors to our ValidationError format
        for error in e.errors():
            field_path = '.'.join(str(loc) for loc in error['loc'])
            errors.append(ValidationError(
                field=field_path,
                error=error['msg'],
                value=str(error.get('input', 'N/A'))
            ))
        return errors
    except Exception as e:
        # Catch any other unexpected errors
        errors.append(ValidationError(
            field='unknown',
            error=f'Unexpected validation error: {str(e)}',
            value=None
        ))
        return errors
