package com.mycoach.app.ui.settings

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.DialogFragment
import androidx.lifecycle.lifecycleScope
import com.mycoach.app.Prefs
import com.mycoach.app.api.ApiClient
import com.mycoach.app.databinding.DialogSettingsBinding
import com.mycoach.app.dataStore
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import androidx.datastore.preferences.core.edit

class SettingsDialog : DialogFragment() {

    private var _binding: DialogSettingsBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = DialogSettingsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Load current URL
        lifecycleScope.launch {
            val prefs = requireContext().dataStore.data.first()
            binding.etServerUrl.setText(prefs[Prefs.SERVER_URL] ?: Prefs.DEFAULT_URL)
        }

        binding.btnSave.setOnClickListener {
            val url = binding.etServerUrl.text.toString().trim()
            if (url.isEmpty()) { Toast.makeText(context, "URL requise", Toast.LENGTH_SHORT).show(); return@setOnClickListener }

            lifecycleScope.launch {
                requireContext().dataStore.edit { it[Prefs.SERVER_URL] = url }
                ApiClient.init(url)
                Toast.makeText(context, "Serveur mis à jour", Toast.LENGTH_SHORT).show()
                dismiss()
            }
        }

        binding.btnCancel.setOnClickListener { dismiss() }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
