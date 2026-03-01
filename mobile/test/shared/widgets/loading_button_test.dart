import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach_mobile/shared/widgets/loading_button.dart';

void main() {
  group('LoadingButton', () {
    testWidgets('renders label', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(body: LoadingButton(label: 'Submit', onPressed: () {})),
      ));
      expect(find.text('Submit'), findsOneWidget);
    });

    testWidgets('shows spinner when loading', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(body: LoadingButton(label: 'Go', onPressed: () {}, isLoading: true)),
      ));
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Go'), findsNothing);
    });

    testWidgets('disabled when loading', (tester) async {
      var pressed = false;
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(body: LoadingButton(label: 'Go', onPressed: () { pressed = true; }, isLoading: true)),
      ));
      await tester.tap(find.byType(ElevatedButton));
      expect(pressed, false);
    });
  });
}
