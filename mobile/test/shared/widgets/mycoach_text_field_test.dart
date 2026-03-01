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

  group('MyCoachTextField – auto password toggle', () {
    testWidgets('shows toggle when obscureText=true and no suffixIcon',
        (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: MyCoachTextField(label: 'Password', obscureText: true),
        ),
      ));
      expect(find.byIcon(Icons.visibility_off), findsOneWidget);
    });

    testWidgets('no toggle when obscureText=false', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(body: MyCoachTextField(label: 'Email')),
      ));
      expect(find.byIcon(Icons.visibility_off), findsNothing);
      expect(find.byIcon(Icons.visibility), findsNothing);
    });

    testWidgets('tapping toggle switches icon', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: MyCoachTextField(label: 'Password', obscureText: true),
        ),
      ));

      expect(find.byIcon(Icons.visibility_off), findsOneWidget);
      await tester.tap(find.byIcon(Icons.visibility_off));
      await tester.pump();
      expect(find.byIcon(Icons.visibility), findsOneWidget);
    });

    testWidgets('double tap restores original icon', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: MyCoachTextField(label: 'Password', obscureText: true),
        ),
      ));

      await tester.tap(find.byIcon(Icons.visibility_off));
      await tester.pump();
      await tester.tap(find.byIcon(Icons.visibility));
      await tester.pump();
      expect(find.byIcon(Icons.visibility_off), findsOneWidget);
    });

    testWidgets('uses custom suffixIcon instead of toggle when provided',
        (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: MyCoachTextField(
            label: 'Password',
            obscureText: true,
            suffixIcon: Icon(Icons.lock),
          ),
        ),
      ));
      // Custom icon shown, not auto-toggle
      expect(find.byIcon(Icons.lock), findsOneWidget);
      expect(find.byIcon(Icons.visibility_off), findsNothing);
    });

    testWidgets('non-password custom suffixIcon works', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: MyCoachTextField(
            label: 'Search',
            suffixIcon: Icon(Icons.search),
          ),
        ),
      ));
      expect(find.byIcon(Icons.search), findsOneWidget);
    });
  });
}
