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

  group('MyCoachTextField – password visibility toggle', () {
    testWidgets('shows visibility_off icon when obscureText is true',
        (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: MyCoachTextField(label: 'Password', obscureText: true),
        ),
      ));
      expect(find.byIcon(Icons.visibility_off), findsOneWidget);
      expect(find.byIcon(Icons.visibility), findsNothing);
    });

    testWidgets('no toggle icon when obscureText is false', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(body: MyCoachTextField(label: 'Email')),
      ));
      expect(find.byIcon(Icons.visibility_off), findsNothing);
      expect(find.byIcon(Icons.visibility), findsNothing);
    });

    testWidgets('tapping eye icon toggles to visibility icon', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: MyCoachTextField(label: 'Password', obscureText: true),
        ),
      ));

      // Initially visibility_off
      expect(find.byIcon(Icons.visibility_off), findsOneWidget);

      // Tap the toggle
      await tester.tap(find.byIcon(Icons.visibility_off));
      await tester.pump();

      // Now shows visibility icon (password revealed)
      expect(find.byIcon(Icons.visibility), findsOneWidget);
      expect(find.byIcon(Icons.visibility_off), findsNothing);
    });

    testWidgets('tapping eye icon twice re-hides password', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: MyCoachTextField(label: 'Password', obscureText: true),
        ),
      ));

      // Tap to show
      await tester.tap(find.byIcon(Icons.visibility_off));
      await tester.pump();
      expect(find.byIcon(Icons.visibility), findsOneWidget);

      // Tap to hide again
      await tester.tap(find.byIcon(Icons.visibility));
      await tester.pump();
      expect(find.byIcon(Icons.visibility_off), findsOneWidget);
    });

    testWidgets('custom suffixIcon is used when not obscureText',
        (tester) async {
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
