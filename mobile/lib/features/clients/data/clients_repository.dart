import '../../../core/api/api_client.dart';
import '../../../shared/models/client.dart';

class ClientsRepository {
  final ApiClient _api;

  ClientsRepository(this._api);

  Future<List<Client>> getClients() async {
    final response = await _api.dio.get('/coaches/clients');
    final list = response.data as List<dynamic>;
    return list.map((e) => Client.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Client> getClient(String id) async {
    final response = await _api.dio.get('/coaches/clients');
    final list = response.data as List<dynamic>;
    final clients = list.map((e) => Client.fromJson(e as Map<String, dynamic>)).toList();
    return clients.firstWhere((c) => c.id == id);
  }

  Future<void> updateClientNote(String clientId, String note) async {
    await _api.dio.put('/coaches/clients/$clientId/note', data: {'note': note});
  }

  // Enrollment tokens
  Future<List<EnrollmentToken>> getEnrollmentTokens() async {
    final response = await _api.dio.get('/coaches/me/enrollment-tokens');
    final list = response.data as List;
    return list.map((e) => EnrollmentToken.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<EnrollmentToken> createEnrollmentToken({String? label, int? maxUses}) async {
    final response = await _api.dio.post('/coaches/me/enrollment-tokens', data: {
      if (label != null) 'label': label,
      if (maxUses != null) 'max_uses': maxUses,
    });
    return EnrollmentToken.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> deleteEnrollmentToken(String tokenId) async {
    await _api.dio.delete('/coaches/me/enrollment-tokens/$tokenId');
  }
}

class EnrollmentToken {
  final String id;
  final String token;
  final String? label;
  final String enrollmentLink;
  final int usesCount;
  final int? maxUses;
  final bool active;

  EnrollmentToken({
    required this.id,
    required this.token,
    this.label,
    required this.enrollmentLink,
    this.usesCount = 0,
    this.maxUses,
    this.active = true,
  });

  factory EnrollmentToken.fromJson(Map<String, dynamic> json) => EnrollmentToken(
        id: json['id'] as String,
        token: json['token'] as String,
        label: json['label'] as String?,
        enrollmentLink: json['enrollment_link'] as String,
        usesCount: (json['uses_count'] as num?)?.toInt() ?? 0,
        maxUses: (json['max_uses'] as num?)?.toInt(),
        active: json['active'] as bool? ?? true,
      );
}
