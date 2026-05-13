import { MantineProvider } from "@mantine/core";
import { render as testingLibraryRender } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

function TestProviders({ children }: { children: React.ReactNode }) {
  return (
    <MantineProvider env="test" defaultColorScheme="light">
      {children}
    </MantineProvider>
  );
}

export function render(ui: React.ReactNode) {
  return testingLibraryRender(ui, { wrapper: TestProviders });
}

export * from "@testing-library/react";
export { userEvent };
