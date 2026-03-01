import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach_mobile/shared/models/client.dart';
import 'package:mycoach_mobile/features/clients/presentation/providers/clients_providers.dart';
import 'package:mycoach_mobile/features/clients/presentation/screens/clients_list_screen.dart';

void main() {
  group('ClientsListScreen', () {
    testWidgets('shows empty state when no clients', (tester) async {
      await tester.pumpWidget(ProviderScope(
        overrides: [
          clientsListProvider.overrideWith((ref) async => <Client>[]),
        ],
        child: const MaterialApp(home: ClientsListScreen()),
      ));
      await tester.pumpAndSettle();
      expect(find.text('Pas encore de clients'), findsOneWidget);
    });

    testWidgets('renders client list', (tester) async {
      final clients = [
        Client(id: 'c1', firstName: 'Jean', lastName: 'Dupont', email: 'j@d.com', createdAt: DateTime(2025)),
        Client(id: 'c2', firstName: 'Marie', lastName: 'Curie', email: 'm@c.com', createdAt: DateTime(2025)),
      ];
      await tester.pumpWidget(ProviderScope(
        overrides: [
          clientsListProvider.overrideWith((ref) async => clients),
        ],
        child: const MaterialApp(home: ClientsListScreen()),
      ));
      await tester.pumpAndSettle();
      expect(find.text('Jean Dupont'), findsOneWidget);
      expect(find.text('Marie Curie'), findsOneWidget);
    });
  });
}
