package com.mycoach.app.ui.sessions

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.mycoach.app.databinding.ItemSessionBinding
import com.mycoach.app.models.Session
import java.text.NumberFormat
import java.util.Locale

class SessionsAdapter(
    private val onDelete: (Session) -> Unit
) : ListAdapter<Session, SessionsAdapter.ViewHolder>(DIFF) {

    private val euroFmt = NumberFormat.getCurrencyInstance(Locale.FRANCE)

    inner class ViewHolder(private val b: ItemSessionBinding) : RecyclerView.ViewHolder(b.root) {
        fun bind(s: Session) {
            b.tvClientName.text = s.clientName
            b.tvDate.text       = s.date
            val h = s.durationMinutes / 60
            val m = s.durationMinutes % 60
            b.tvDuration.text   = if (m > 0) "${h}h${m}m" else "${h}h"
            b.tvAmount.text     = if (s.billed) euroFmt.format(s.amount) else "Non facturé"
            if (s.notes != null) {
                b.tvNotes.visibility = ViewGroup.VISIBLE
                b.tvNotes.text = s.notes
            } else {
                b.tvNotes.visibility = ViewGroup.GONE
            }
            b.root.setOnLongClickListener { onDelete(s); true }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        ViewHolder(ItemSessionBinding.inflate(LayoutInflater.from(parent.context), parent, false))

    override fun onBindViewHolder(holder: ViewHolder, position: Int) = holder.bind(getItem(position))

    companion object {
        val DIFF = object : DiffUtil.ItemCallback<Session>() {
            override fun areItemsTheSame(a: Session, b: Session) = a.id == b.id
            override fun areContentsTheSame(a: Session, b: Session) = a == b
        }
    }
}
