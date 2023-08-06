import { useMemo } from "react";
import { observer } from "mobx-react-lite";

import { getRandomHash } from "@carefree0910/core";

import type { IPlugin } from "@/schema/plugins";
import { onArrange } from "@/actions/arrange";
import { drawboardPluginFactory } from "../utils/factory";
import Render from "../components/Render";

const ArrangePlugin = ({ pluginInfo: { nodes }, ...props }: IPlugin) => {
  const id = useMemo(() => `arrange_${getRandomHash()}`, []);

  return (
    <Render
      id={id}
      onFloatingButtonClick={async () => onArrange({ type: "multiple", nodes })}
      {...props}
    />
  );
};
drawboardPluginFactory.register("arrange", true)(observer(ArrangePlugin));
