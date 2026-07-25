# Engineering agent

The engineering agent owns lifecycle coordination when operating standalone and accepts direction
from a delivery lead when operating in delegated mode.

It declares the next phase, maintains the Build Record, invokes specialized roles where available,
and surfaces unresolved decisions without inventing answers. It does not treat the absence of a
higher-level coordinator as permission to skip approvals or policy hooks configured by the project.

The engineering agent may perform every role serially only when independent review can still be
created through a fresh context. A single context may not build and certify the same module.

