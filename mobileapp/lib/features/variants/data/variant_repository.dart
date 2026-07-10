import 'package:dio/dio.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/app_error.dart';
import '../../../core/network/dio_client.dart';
import 'variant_models.dart';

/// Repository for all AI variant operations.
/// All approval-gated and generate methods always hit the network.
class VariantRepository {
  const VariantRepository({required DioClient dioClient})
      : _client = dioClient;

  final DioClient _client;

  // ── Generate ──────────────────────────────────────────────────────────────

  Future<VariantRecord> generate(GenerateVariantRequest request) async {
    try {
      final response = await _client.dio.post(
        ApiEndpoints.aiGenerate,
        data: request.toJson(),
      );
      return VariantRecord.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  // ── List pending ──────────────────────────────────────────────────────────

  Future<PendingVariantsResponse> getPendingVariants(String userId) async {
    try {
      final response =
          await _client.dio.get(ApiEndpoints.aiPending(userId));
      return PendingVariantsResponse.fromJson(
          response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  // ── Preview ───────────────────────────────────────────────────────────────

  Future<VariantPreview> getPreview(String variantId) async {
    try {
      final response =
          await _client.dio.get(ApiEndpoints.aiPreview(variantId));
      return VariantPreview.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  // ── Approval token — NEVER cached ────────────────────────────────────────

  /// Always fetches a fresh token from the server. Must be called immediately
  /// before opening the approval sheet. Result must not be stored locally.
  Future<String> fetchApprovalToken(String variantId) async {
    try {
      final response = await _client.dio.get(
        ApiEndpoints.aiVariantToken(variantId),
      );
      final token = response.data['approval_token'] as String?;
      if (token == null) {
        throw AppError.unknown('Approval token missing from response.');
      }
      return token;
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  // ── Approve ───────────────────────────────────────────────────────────────

  Future<ApproveVariantResponse> approve(
    String variantId,
    String approvalToken,
  ) async {
    try {
      final response = await _client.dio.post(
        ApiEndpoints.aiApprove(variantId),
        data: {'approval_token': approvalToken},
      );
      return ApproveVariantResponse.fromJson(
          response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  // ── Reject ────────────────────────────────────────────────────────────────

  Future<void> reject(String variantId, {String? userFeedback}) async {
    try {
      await _client.dio.post(
        ApiEndpoints.aiReject(variantId),
        data: RejectVariantRequest(userFeedback: userFeedback).toJson(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }
}
