import 'package:dio/dio.dart';

/// Codes d'erreur métier retournés par le backend.
enum ApiErrorCode {
  emailAlreadyExists,
  phoneAlreadyExists,
  blockedEmailDomain,
  invalidCredentials,
  emailNotVerified,
  accountSuspended,
  tooManyAttempts,
  invalidOtp,
  otpMaxAttempts,
  noCreditsAvailable,
  enrollmentTokenInvalid,
  unknown,
}

/// Exception API unifiée — wrappée par [ApiKeyInterceptor.onError].
class AppDioException extends DioException {
  AppDioException({
    required super.requestOptions,
    super.response,
    super.type,
    super.error,
    required this.code,
    this.userMessage,
    this.retryAfterSeconds,
  }) : super(message: code.name);

  /// Code métier parsé depuis la réponse JSON.
  final ApiErrorCode code;

  /// Message lisible (si disponible dans la réponse).
  final String? userMessage;

  /// Secondes avant réessai (pour 429).
  final int? retryAfterSeconds;

  static ApiErrorCode _parseCode(String? raw) => switch (raw) {
    'email_already_exists'     => ApiErrorCode.emailAlreadyExists,
    'phone_already_exists'     => ApiErrorCode.phoneAlreadyExists,
    'blocked_email_domain'     => ApiErrorCode.blockedEmailDomain,
    'invalid_credentials'      => ApiErrorCode.invalidCredentials,
    'email_not_verified'       => ApiErrorCode.emailNotVerified,
    'account_suspended'        => ApiErrorCode.accountSuspended,
    'too_many_attempts'        => ApiErrorCode.tooManyAttempts,
    'invalid_otp'              => ApiErrorCode.invalidOtp,
    'otp_max_attempts'         => ApiErrorCode.otpMaxAttempts,
    'no_credits_available'     => ApiErrorCode.noCreditsAvailable,
    'enrollment_token_invalid' => ApiErrorCode.enrollmentTokenInvalid,
    _                          => ApiErrorCode.unknown,
  };

  factory AppDioException.fromDio(DioException e) {
    final data = e.response?.data;
    String? rawCode;
    String? userMsg;
    int? retryAfter;

    if (data is Map<String, dynamic>) {
      rawCode  = data['detail'] is String ? data['detail'] as String : null;
      userMsg  = data['message'] as String?;
      retryAfter = data['retry_after'] as int?;
    }

    return AppDioException(
      requestOptions: e.requestOptions,
      response:       e.response,
      type:           e.type,
      error:          e.error,
      code:           _parseCode(rawCode),
      userMessage:    userMsg,
      retryAfterSeconds: retryAfter,
    );
  }

  /// `true` si l'API Key est révoquée / absente → déconnexion forcée.
  bool get isUnauthorized => response?.statusCode == 401;

  /// `true` si limite de débit atteinte.
  bool get isRateLimit => response?.statusCode == 429;

  /// `true` si paiement requis (pas de crédit).
  bool get isPaymentRequired => response?.statusCode == 402;
}
