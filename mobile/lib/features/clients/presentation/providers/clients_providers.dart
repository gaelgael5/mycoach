import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../shared/models/client.dart';
import '../../data/clients_repository.dart';

final clientsRepositoryProvider = Provider<ClientsRepository>((ref) {
  return ClientsRepository(ref.watch(apiClientProvider));
});

final clientsListProvider = FutureProvider<List<Client>>((ref) async {
  return ref.watch(clientsRepositoryProvider).getClients();
});

final clientDetailProvider = FutureProvider.family<Client, String>((ref, id) async {
  return ref.watch(clientsRepositoryProvider).getClient(id);
});
