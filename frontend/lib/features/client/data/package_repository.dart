import 'package:dio/dio.dart';
import '../../../shared/models/package.dart';
import '../../../shared/models/payment.dart';

class PackageRepository {
  const PackageRepository(this._dio);

  final Dio _dio;

  Future<List<Package>> getAvailablePackages() async {
    final resp = await _dio.get<List<dynamic>>('/packages/available');
    return (resp.data ?? [])
        .map((e) => Package.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<MyPackageBalance> getMyBalance() async {
    final resp = await _dio.get<Map<String, dynamic>>('/packages/me');
    return MyPackageBalance.fromJson(resp.data!);
  }

  Future<Map<String, dynamic>> purchasePackage({
    required String packageId,
    required String paymentMethod,
  }) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/packages/purchase',
      data: {
        'package_id': packageId,
        'payment_method': paymentMethod,
      },
    );
    return resp.data!;
  }

  Future<({List<Payment> payments, int total})> getPaymentHistory({
    int page = 1,
    int limit = 20,
  }) async {
    final resp = await _dio.get<Map<String, dynamic>>(
      '/payments/me',
      queryParameters: {'page': page, 'limit': limit},
    );
    final data = resp.data!;
    final payments = (data['payments'] as List<dynamic>)
        .map((e) => Payment.fromJson(e as Map<String, dynamic>))
        .toList();
    return (
      payments: payments,
      total: data['total'] as int? ?? payments.length,
    );
  }
}
