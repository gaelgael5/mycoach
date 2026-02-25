package com.mycoach.app.ui.payments
import android.os.Bundle; import android.view.*; import android.widget.Toast
import androidx.fragment.app.Fragment; import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.mycoach.app.R; import com.mycoach.app.api.ApiClient
import com.mycoach.app.databinding.FragmentPaymentsBinding
import com.mycoach.app.models.PaymentRequest
import kotlinx.coroutines.*
import java.text.SimpleDateFormat; import java.util.*
class PaymentsFragment : Fragment() {
    private var _b: FragmentPaymentsBinding? = null; private val b get() = _b!!
    private val vm: PaymentsViewModel by viewModels()
    private val adapter = PaymentsAdapter { p ->
        MaterialAlertDialogBuilder(requireContext()).setTitle("Supprimer ce paiement ?")
            .setPositiveButton("Supprimer") { _,_ -> vm.delete(p.id) }.setNegativeButton("Annuler",null).show()
    }
    override fun onCreateView(i: LayoutInflater, c: ViewGroup?, s: Bundle?): View { _b = FragmentPaymentsBinding.inflate(i,c,false); return b.root }
    override fun onViewCreated(v: View, s: Bundle?) {
        super.onViewCreated(v, s)
        b.recyclerView.layoutManager = LinearLayoutManager(context); b.recyclerView.adapter = adapter
        b.swipeRefresh.setOnRefreshListener { vm.load() }
        b.fab.setOnClickListener { showAddDialog() }
        vm.loading.observe(viewLifecycleOwner) { b.progressBar.visibility = if (it) View.VISIBLE else View.GONE; if (!it) b.swipeRefresh.isRefreshing = false }
        vm.error.observe(viewLifecycleOwner) { if (it != null) Toast.makeText(context, it, Toast.LENGTH_LONG).show() }
        vm.payments.observe(viewLifecycleOwner) { pmts -> adapter.submitList(pmts); b.tvEmpty.visibility = if (pmts.isEmpty()) View.VISIBLE else View.GONE; b.tvEmpty.text = getString(R.string.no_payments) }
        vm.load()
    }
    private fun showAddDialog() {
        CoroutineScope(Dispatchers.Main).launch {
            val clients = try { withContext(Dispatchers.IO) { ApiClient.service.getClients() } } catch (e: Exception) { Toast.makeText(context, e.message, Toast.LENGTH_SHORT).show(); return@launch }
            if (clients.isEmpty()) { Toast.makeText(context, "Ajoutez d'abord un client", Toast.LENGTH_SHORT).show(); return@launch }
            val names = clients.map { "${it.name} (solde: ${it.balance}€)" }.toTypedArray()
            var selectedIdx = 0
            val today = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Date())
            MaterialAlertDialogBuilder(requireContext()).setTitle("Enregistrer un paiement").setSingleChoiceItems(names, 0) { _,i -> selectedIdx = i }
                .setPositiveButton("Ajouter (montant à préciser)") { _,_ ->
                    vm.create(PaymentRequest(clientId = clients[selectedIdx].id, date = today, amount = 0.0, method = null))
                }.setNegativeButton(getString(R.string.cancel), null).show()
        }
    }
    override fun onDestroyView() { super.onDestroyView(); _b = null }
}
