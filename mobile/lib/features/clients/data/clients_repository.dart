import '../../../core/api/api_client.dart';
import '../../../shared/models/client.dart';

class ClientsRepository {
  final ApiClient _api;

  ClientsRepository(this._api);

  Future<List<Client>> getClients() async {
    final response = await _api.dio.get('/clients');
    final list = response.data as List<dynamic>;
    return list.map((e) => Client.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Client> getClient(String id) async {
    final response = await _api.dio.get('/clients/$id');
    return Client.fromJson(response.data as Map<String, dynamic>);
  }
}
