import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach_mobile/shared/widgets/mycoach_text_field.dart';

void main() {
  group('MyCoachTextField', () {
    testWidgets('renders label', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(body: MyCoachTextField(label: 'Email')),
      ));
      expect(find.text('Email'), findsOneWidget);
    });

    testWidgets('accepts input', (tester) async {
      final ctrl = TextEditingController();
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(body: MyCoachTextField(label: 'Name', controller: ctrl)),
      ));
      await tester.enterText(find.byType(TextFormField), 'Hello');
      expect(ctrl.text, 'Hello');
    });

    testWidgets('shows hint', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(body: MyCoachTextField(label: 'X', hint: 'Type here')),
      ));
      expect(find.text('Type here'), findsOneWidget);
    });
  });
}
