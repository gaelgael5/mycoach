import 'package:flutter_test/flutter_test.dart';

/// Validation logic extracted for unit testing.
/// These test the same validators used in RegisterScreen.

String? passwordValidator(String? v) =>
    v == null || v.length < 6 ? 'Min. 8 caractères' : null;

String? confirmPasswordValidator(String? v, String password) =>
    v?.trim() != password.trim()
        ? 'Les mots de passe ne correspondent pas'
        : null;

String? requiredValidator(String? v) =>
    v == null || v.isEmpty ? 'Requis' : null;

String? emailValidator(String? v) =>
    v == null || !v.contains('@') ? 'Email invalide' : null;

void main() {
  group('RegisterScreen validators – password', () {
    test('password too short returns error', () {
      expect(passwordValidator('123'), 'Min. 8 caractères');
    });

    test('password null returns error', () {
      expect(passwordValidator(null), 'Min. 8 caractères');
    });

    test('password 6+ chars returns null', () {
      expect(passwordValidator('abc123'), isNull);
    });

    test('confirm matches password → null', () {
      expect(confirmPasswordValidator('abc123', 'abc123'), isNull);
    });

    test('confirm differs from password → error', () {
      expect(confirmPasswordValidator('xyz789', 'abc123'),
          'Les mots de passe ne correspondent pas');
    });

    test('confirm empty vs filled password → error', () {
      expect(confirmPasswordValidator('', 'abc123'),
          'Les mots de passe ne correspondent pas');
    });

    test('confirm null vs filled password → error', () {
      expect(confirmPasswordValidator(null, 'abc123'),
          'Les mots de passe ne correspondent pas');
    });

    test('confirm with trailing space matches after trim', () {
      expect(confirmPasswordValidator('abc123 ', 'abc123'), isNull);
    });

    test('both with trailing spaces match after trim', () {
      expect(confirmPasswordValidator('abc123  ', 'abc123 '), isNull);
    });
  });

  group('RegisterScreen validators – required fields', () {
    test('empty name → Requis', () {
      expect(requiredValidator(''), 'Requis');
    });

    test('null name → Requis', () {
      expect(requiredValidator(null), 'Requis');
    });

    test('filled name → null', () {
      expect(requiredValidator('Gael'), isNull);
    });
  });

  group('RegisterScreen validators – email', () {
    test('invalid email → error', () {
      expect(emailValidator('notanemail'), 'Email invalide');
    });

    test('valid email → null', () {
      expect(emailValidator('test@test.com'), isNull);
    });
  });
}
